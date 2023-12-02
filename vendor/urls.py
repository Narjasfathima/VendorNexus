from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import SignUpViewset,VendorViewSet,PurchaseOrderViewSet

router=DefaultRouter()
router.register('user',SignUpViewset,basename='user')
router.register('vendors',VendorViewSet,basename='vendors')
router.register('purchase_orders',PurchaseOrderViewSet,basename='purchase_orders')

urlpatterns=[
   
]+router.urls