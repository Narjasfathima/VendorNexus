from django.db import models
from django.contrib.auth.models import User
import random
import string
from django.core.validators import MinValueValidator, RegexValidator

# Create your models here.

# For storing Vendor details
class Vendor(models.Model):
    name = models.CharField(max_length=255)
    contact_details = models.TextField()
    address = models.TextField()
    vendor_code = models.CharField(max_length=50, unique=True, editable=False)
    on_time_delivery_rate = models.FloatField(default=0,validators=[MinValueValidator(0, message="Delivery rate must be 0 or greater.")])
    quality_rating_avg = models.FloatField(default=0,validators=[MinValueValidator(0, message="Quality rate must be 0 or greater.")])
    average_response_time = models.FloatField(default=0,validators=[MinValueValidator(0, message="Response time must be 0 or greater.")])
    fulfillment_rate = models.FloatField(default=0,validators=[MinValueValidator(0, message="Fullfillment rate must be 0 or greater.")]) 

    def save(self, *args, **kwargs):
        if not self.vendor_code:
            
            # If you want to use random.choice with string.ascii_letters and string.digits
            random_string = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8))

            self.vendor_code = f"VENDOR-{random_string}"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.vendor_code
    


# For storing Purchase Order 
class PurchaseOrder(models.Model):
    po_number = models.CharField(max_length=50, unique=True, editable=False)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    order_date = models.DateTimeField()
    delivery_date = models.DateTimeField()
    items = models.JSONField()
    quantity = models.IntegerField()
    status = models.CharField(max_length=50)
    quality_rating = models.FloatField(null=True, blank=True)
    issue_date = models.DateTimeField()
    acknowledgment_date = models.DateTimeField(null=True, blank=True)


    def save(self, *args, **kwargs):
        if not self.po_number:

            # If you want to use random.choice with string.ascii_letters and string.digits
            random_string = ''.join(random.choice(string.digits) for _ in range(8))
            self.po_number = f"PO-{random_string}"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.po_number
    

# For storing Historical Performance 
class HistoricalPerformance(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    on_time_delivery_rate = models.FloatField(null=True)
    quality_rating_avg = models.FloatField(null=True)
    average_response_time = models.FloatField(null=True)
    fulfillment_rate = models.FloatField(null=True)

    def __str__(self):
        return f"{self.vendor} - {self.date}"


# For storing Actual Delivery date  
class DeliveryRecord(models.Model):
    purchase_order=models.ForeignKey(PurchaseOrder,on_delete=models.CASCADE)
    is_delivered_on_date=models.BooleanField()
    date=models.DateTimeField(auto_now_add=True)

