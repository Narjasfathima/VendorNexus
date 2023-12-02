from rest_framework import serializers

from django.contrib.auth.models import User

from django.core.exceptions import ValidationError

from datetime import datetime
from django.utils import timezone

from .models import Vendor,PurchaseOrder,HistoricalPerformance




# User Model Serializer
class UserModelSer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['username','password','email']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
    


# Vendor model serializer for creating, listing and  updating  vendor
class VendorModelSer(serializers.ModelSerializer):
    id=serializers.CharField(read_only=True)
    vendor_code=serializers.CharField(read_only=True)

    class Meta:
        model=Vendor
        fields=['id','name','contact_details','address','vendor_code']



# Purchase Order  model serializer for creating, listing and  updating  purchase orders of vendor
class PurchaseOrderModelSer(serializers.ModelSerializer):
    id=serializers.CharField(read_only=True)
    po_number=serializers.CharField(read_only=True)
    quality_rating=serializers.FloatField(required=False)
    acknowledgment_date=serializers.DateTimeField(required=False)
    class Meta:
        model=PurchaseOrder
        fields='__all__'

    def validate_vendor(self, value):
        if not isinstance(value, Vendor):
            raise serializers.ValidationError("Vendor with the specified ID does not exist.")
        
        return value
        
    def validate_order_date(self, value):
        if not timezone.is_aware(value):
                value = timezone.make_aware(value)
        return value

    def validate_delivery_date(self, value):
        try:
            order_date_str = self.initial_data.get('order_date')
            
            if order_date_str:
                # Convert order_date string to datetime object in UTC timezone
                order_date = timezone.make_aware(datetime.strptime(order_date_str, '%Y-%m-%dT%H:%M:%S.%fZ'))

                # Convert value to UTC timezone if it's timezone-naive
                if not timezone.is_aware(value):
                    value = timezone.make_aware(value)
                    print(value)

                # Compare datetime objects
                if value <= order_date:
                    raise serializers.ValidationError("Delivery date must be greater than the order date.")

            return value
        
        except:
            raise serializers.ValidationError("Order date is invalid.")
    
    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0.")

        return value
    
    def validate_status(self, value):
        valid_statuses = ["ordered", "dispatched", "shipped", "pending", "canceled", "completed"]

        if value not in valid_statuses:
            raise serializers.ValidationError("Invalid status. Allowed values are: ordered, dispatched, shipped, pending, canceled, completed.")

        return value
    
    def validate_quality_rating(self, value):
        if value < 0:
            raise serializers.ValidationError("Quality rating must be null or greater than or equal to 0.")
        return value
    
    def validate_issue_date(self, value):
        if not timezone.is_aware(value):
                value = timezone.make_aware(value)
        return value
    
    def validate_acknowledgment_date(self, value):
        try:
            issue_date_str = self.initial_data.get('issue_date')

            if issue_date_str:
                # Convert issue_date string to datetime object in UTC timezone
                issue_date = timezone.make_aware(datetime.strptime(issue_date_str, '%Y-%m-%dT%H:%M:%S.%fZ'))
            
                # Convert value to UTC timezone if it's timezone-naive
                if not timezone.is_aware(value):
                    value = timezone.make_aware(value)

                # Compare datetime objects
                if value <= issue_date:
                    raise serializers.ValidationError("Acknowledgment date must be null or greater than the issue date.")            

            return value
        
        except:
            raise serializers.ValidationError("Issue date is invalid.")

    def validate(self, data):
        # Validate the entire serializer data
        errors = {}

        try:
            self.validate_vendor(data['vendor'])
        except ValidationError as e:
            errors['vendor'] = e.detail

        try:
            self.validate_order_date(data['order_date'])
        except ValidationError as e:
            errors['order_date'] = e.detail
            print(errors['order_date'])

        try:
            self.validate_delivery_date(data['delivery_date'])
        except ValidationError as e:
            errors['delivery_date'] = e.detail

        try:
            self.validate_quantity(data['quantity'])
        except ValidationError as e:
            errors['quantity'] = e.detail

        try:
            self.validate_status(data['status'])
        except ValidationError as e:
            errors['status'] = e.detail

        try:
            quality_rating = data.get('quality_rating')
            if quality_rating is not None:
                self.validate_quality_rating(quality_rating)
        except ValidationError as e:
            errors['quality_rating'] = e.detail

        try:
            self.validate_issue_date(data['issue_date'])
        except ValidationError as e:
            errors['issue_date'] = e.detail

        try:
            acknowledgment_date = data.get('acknowledgment_date')
            if acknowledgment_date is not None:
                self.validate_acknowledgment_date(acknowledgment_date)
        except ValidationError as e:
            errors['acknowledgment_date'] = e.detail

        if errors:
            raise serializers.ValidationError(errors)

        return data
    


# Performance metric serializer for listing performance
class PerformanceModelSer(serializers.ModelSerializer):
    vendor=VendorModelSer(read_only=True)
    class Meta:
        model=HistoricalPerformance
        fields=['vendor','on_time_delivery_rate','quality_rating_avg','average_response_time','fulfillment_rate']



# Acknowledgement  serializer for adding  acknowledgement date
class AcknowledgeModelSer(serializers.ModelSerializer):
    class Meta:
        model=PurchaseOrder
        fields=['acknowledgment_date']

    def validate_acknowledgment_date(self, value):
        # If acknowledgment_date is being updated
        if self.instance.acknowledgment_date is not None and value is not None:
            issue_date = self.instance.issue_date

            if issue_date:
                # Convert value to UTC timezone if it's timezone-naive
                if not timezone.is_aware(value):
                    value = timezone.make_aware(value)

                # Compare datetime objects
                if value <= issue_date:
                    raise serializers.ValidationError("Acknowledgment date must be null or greater than the issue date.")

        return value
