from django.test import TestCase
from ..models import Vendor, PurchaseOrder, HistoricalPerformance, DeliveryRecord
from django.utils import timezone

class VendorModelTest(TestCase):

    def test_vendor_creation(self):
        vendor = Vendor.objects.create(
            name="Test Vendor",
            contact_details="Test Contact Details",
            address="Test Address"
        )
        self.assertEqual(vendor.name, "Test Vendor")
        self.assertEqual(vendor.on_time_delivery_rate, 0)  


class PurchaseOrderModelTest(TestCase):

    def test_purchase_order_creation(self):
        vendor = Vendor.objects.create(
            name="Test Vendor",
            contact_details="Test Contact Details",
            address="Test Address"
        )
        purchase_order = PurchaseOrder.objects.create(
            vendor=vendor,
            order_date=timezone.now(),
            delivery_date=timezone.now() + timezone.timedelta(days=7),
            items={"item": "Test Item"},
            quantity=10,
            status="pending",
            issue_date=timezone.now()
        )
        self.assertTrue(purchase_order.po_number.startswith("PO-"))
        self.assertEqual(purchase_order.vendor, vendor)
        self.assertEqual(purchase_order.status, "pending")



class HistoricalPerformanceModelTest(TestCase):

    def test_historical_performance_creation(self):
        vendor = Vendor.objects.create(
            name="Test Vendor",
            contact_details="Test Contact Details",
            address="Test Address"
        )
        historical_performance = HistoricalPerformance.objects.create(
            vendor=vendor,
            on_time_delivery_rate=0.75,
            quality_rating_avg=4.5,
            average_response_time=24.5,
            fulfillment_rate=0.85
        )
        self.assertEqual(historical_performance.vendor, vendor)
        self.assertEqual(historical_performance.on_time_delivery_rate, 0.75)




class DeliveryRecordModelTest(TestCase):

    def test_delivery_record_creation(self):
        vendor = Vendor.objects.create(
            name="Test Vendor",
            contact_details="Test Contact Details",
            address="Test Address"
        )
        purchase_order = PurchaseOrder.objects.create(
            vendor=vendor,
            order_date=timezone.now(),
            delivery_date=timezone.now() + timezone.timedelta(days=7),
            items={"item": "Test Item"},
            quantity=10,
            status="completed",
            issue_date=timezone.now(),
            acknowledgment_date=timezone.now()
        )
        delivery_record = DeliveryRecord.objects.create(
            purchase_order=purchase_order,
            is_delivered_on_date=True
        )
        self.assertEqual(delivery_record.purchase_order, purchase_order)
        self.assertTrue(delivery_record.is_delivered_on_date)
