from django.db.models.signals import post_save,pre_save,post_delete
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from datetime import timedelta
from django.utils import timezone
from django.db.models import F
from .models import PurchaseOrder, Vendor, HistoricalPerformance,DeliveryRecord


channel_layer = get_channel_layer()

@receiver(pre_save, sender=PurchaseOrder)
def capture_previous_status(sender, instance, **kwargs):
    if instance.pk:
        # Get the second-to-last value of the 'status' field
        previous_status = PurchaseOrder.objects.filter(pk=instance.pk).order_by('-id').values_list('status', flat=True).first()

        # Get the second-to-last delivery date using F expressions
        previous_delivery_date = PurchaseOrder.objects.filter(pk=instance.pk).order_by('-id').values_list(F('delivery_date'), flat=True).first()

        # Store the previous status and delivery date values in the instance for later use
        instance._previous_status = previous_status if previous_status else 'unknown'
        instance._previous_delivery_date = previous_delivery_date


@receiver([post_save], sender=PurchaseOrder)
def handle_po_update(sender, instance, **kwargs):
    
    if instance.status is not None:
        update_on_time_delivery_rate(instance,instance.vendor)

    if instance.quality_rating is not None:
        update_quality_rating_avg(instance.vendor)
        
    if instance.acknowledgment_date:
        update_average_response_time(instance.vendor)

    if instance.status:   
        update_fulfillment_rate(instance.vendor)

    performance=HistoricalPerformance.objects.filter(vendor=instance.vendor).first()
    if performance:
        performance.date=timezone.now()
        performance.on_time_delivery_rate=instance.vendor.on_time_delivery_rate
        performance.quality_rating_avg=instance.vendor.quality_rating_avg
        performance.average_response_time=instance.vendor.average_response_time
        performance.fulfillment_rate=instance.vendor.fulfillment_rate
        performance.save()
    else:
        HistoricalPerformance.objects.create(vendor=instance.vendor,
                                             on_time_delivery_rate=instance.vendor.on_time_delivery_rate,
                                             quality_rating_avg=instance.vendor.quality_rating_avg,
                                             average_response_time=instance.vendor.average_response_time,
                                             fulfillment_rate=instance.vendor.fulfillment_rate)
    
    # Send a message to WebSocket consumers
    async_to_sync(channel_layer.group_send)(
        "metrics_group",
        {"type": "update.metric", "message": "Metrics updated"},
    )


def update_quality_rating_avg(vendor):
    completed_pos = PurchaseOrder.objects.filter(vendor=vendor, quality_rating__isnull=False)
    quality_ratings = [po.quality_rating for po in completed_pos]
    avg_quality_rating = sum(quality_ratings) / len(quality_ratings) if quality_ratings else 0
    vendor.quality_rating_avg = avg_quality_rating
    vendor.save()


def update_average_response_time(vendor):
    acknowledged_pos = PurchaseOrder.objects.filter(vendor=vendor, acknowledgment_date__isnull=False)
    response_times = [po.acknowledgment_date - po.issue_date for po in acknowledged_pos]
    avg_response_time = sum(response_times, timedelta()) / len(response_times) if response_times else timedelta()
    vendor.average_response_time = avg_response_time.total_seconds() / 3600  # in hours
    vendor.save()


def update_fulfillment_rate(vendor):
    completed_pos = PurchaseOrder.objects.filter(vendor=vendor)
    successful_fulfillments = completed_pos.filter(acknowledgment_date__isnull=False,status='completed')
    fulfillment_rate = successful_fulfillments.count() / completed_pos.count() if completed_pos else 0
    vendor.fulfillment_rate = fulfillment_rate
    vendor.save()


def update_on_time_delivery_rate(instance,vendor):
        try:
            previous_status = getattr(instance, '_previous_status', None)
            previous_delivery_date = getattr(instance, '_previous_delivery_date', None)

            completed_pos = PurchaseOrder.objects.filter(vendor=vendor, status='completed')
            no_completed_pos = completed_pos.count() if completed_pos else 0

            if instance.status == 'completed' and previous_status != 'completed':            
                actual_delivery_date=timezone.now()

                delivery_date = instance.delivery_date
                if not timezone.is_aware(delivery_date):
                    delivery_date = timezone.make_aware(delivery_date)

                if actual_delivery_date <= delivery_date:
                    delivery_record=DeliveryRecord.objects.filter(purchase_order=instance).first()

                    if delivery_record:
                        delivery_record.is_delivered_on_date=True
                        delivery_record.save()
                    else:
                        DeliveryRecord.objects.create(purchase_order=instance,is_delivered_on_date=True,vendor=vendor)

                delivery_count=DeliveryRecord.objects.filter(is_delivered_on_date=True,vendor=vendor).count()
                new_on_time_delivery_rate = delivery_count / no_completed_pos if no_completed_pos != 0 else 0 
                print(f"New on_time_delivery_rate: {new_on_time_delivery_rate}")

                vendor.on_time_delivery_rate = new_on_time_delivery_rate
                vendor.save()
                print(vendor.on_time_delivery_rate)

            elif instance.status != 'completed' and previous_status == 'completed':
                delivery_record=DeliveryRecord.objects.get(purchase_order=instance)
                delivery_record.delete()

                delivery_count=DeliveryRecord.objects.filter(is_delivered_on_date=True,vendor=vendor).count()
                new_on_time_delivery_rate = delivery_count / no_completed_pos if no_completed_pos != 0 else 0 
                print(f"New on_time_delivery_rate: {new_on_time_delivery_rate}")

                vendor.on_time_delivery_rate = new_on_time_delivery_rate
                vendor.save()
                print(vendor.on_time_delivery_rate)

            elif instance.status == 'completed' and previous_status == 'completed' and instance.delivery_date != previous_delivery_date:
                delivery_record=DeliveryRecord.objects.get(purchase_order=instance)
                actual_delivery_date=delivery_record.date

                delivery_date = instance.delivery_date
                if not timezone.is_aware(delivery_date):
                    delivery_date = timezone.make_aware(delivery_date)

                if actual_delivery_date <= delivery_date:
                        delivery_record.is_delivered_on_date=True
                        delivery_record.save()
                else:
                    delivery_record.delete()
            
            else:
                return
  
        except Exception as e:
            print(f"Error in update_on_time_delivery_rate: {e}")


@receiver([post_delete], sender=PurchaseOrder)
def handle_po_delete(sender, instance, **kwargs):

    if instance.quality_rating is not None:
        update_quality_rating_avg(instance.vendor)

    if instance.status == 'completed':
        update_on_time_delivery_rate_1(instance,instance.vendor)

    if instance.acknowledgment_date:
        update_average_response_time(instance.vendor)

    if instance.status:   
        update_fulfillment_rate(instance.vendor)

        performance=HistoricalPerformance.objects.filter(vendor=instance.vendor).first()
        if performance:
            performance.date=timezone.now()
            performance.on_time_delivery_rate=instance.vendor.on_time_delivery_rate
            performance.quality_rating_avg=instance.vendor.quality_rating_avg
            performance.average_response_time=instance.vendor.average_response_time
            performance.fulfillment_rate=instance.vendor.fulfillment_rate
            performance.save()

    # Send a message to WebSocket consumers
    async_to_sync(channel_layer.group_send)(
        "metrics_group",
        {"type": "update.metric", "message": "Metrics updated"},
    )

def update_on_time_delivery_rate_1(instance,vendor):
    try:            
        completed_pos = PurchaseOrder.objects.filter(vendor=vendor, status='completed')
        no_completed_pos = completed_pos.count() if completed_pos else 0

        
        delivery_count=DeliveryRecord.objects.filter(vendor=vendor,is_delivered_on_date=True).count()

        new_on_time_delivery_rate = delivery_count / no_completed_pos if no_completed_pos != 0 else 0 
        print(f"New on_time_delivery_rate: {new_on_time_delivery_rate}")

        vendor.on_time_delivery_rate = new_on_time_delivery_rate
        vendor.save()
        print(vendor.on_time_delivery_rate) 

    except Exception as e:
            print(f"Error in update_on_time_delivery_rate: {e}")
