from django.shortcuts import render

from rest_framework.viewsets import ViewSet

from rest_framework.response import Response

from rest_framework import status

from rest_framework.exceptions import ValidationError

from rest_framework.decorators import action

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from drf_yasg.inspectors import SwaggerAutoSchema

from rest_framework.authentication import TokenAuthentication
from rest_framework import permissions

from .models import Vendor,PurchaseOrder,HistoricalPerformance

from .serializers import UserModelSer,VendorModelSer,PurchaseOrderModelSer,PerformanceModelSer,AcknowledgeModelSer
# Create your views here.



# Signup Viewset
class SignUpViewset(ViewSet):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD),
                'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
                 },
            required=['username', 'password', 'email'],
                    ),
        responses={201: "Your Response Description"},
    )
    def create(self,request):
        ser=UserModelSer(data=request.data)
        if ser.is_valid():
            ser.save()
            return Response({"message":"Account created"})
        return Response({"message":"Failed"})
    

# Vendor viewset
class VendorViewSet(ViewSet):
    authentication_classes=[TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]

    # Create a new vendor.
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING),
                'contact_details': openapi.Schema(type=openapi.TYPE_STRING),
                'address': openapi.Schema(type=openapi.TYPE_STRING),
                 },
            required=['name', 'contact_details', 'address'],
                    ),
        responses={201: "Vendor created"},
    )
    def create(self,request):
        try:
            ser=VendorModelSer(data=request.data)
            if ser.is_valid():
                ser.save()
                return Response({"msg":"Vendor created"},status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({"msg": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    # List all vendors.
    def list(self,request):
        try:
            vendor=Vendor.objects.all()
            dser=VendorModelSer(vendor,many=True)
            return Response(data=dser.data)
        
        except Exception as e:
            return Response({"msg": "Failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

    # Retrieve a specific vendor's details.
    def retrieve(self,request,*args,**kwargs):
        vid=kwargs.get('pk')
        try:
            vendor=Vendor.objects.get(id=vid)
            dser=VendorModelSer(vendor)
            return Response(data=dser.data)
        except Vendor.DoesNotExist:
            return Response({"msg": f"Vendor with ID {vid} not found"}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({"msg": "Failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

    # Update a vendor's details.
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING),
                'contact_details': openapi.Schema(type=openapi.TYPE_STRING),
                'address': openapi.Schema(type=openapi.TYPE_STRING),
                 },
            required=['name', 'contact_details', 'address'],
                    ),
        responses={202: "Vendor Details Updated"},
    )
    def update(self,request,*args,**kwargs):
        vid=kwargs.get('pk')
        try:
            vendor=Vendor.objects.get(id=vid)
            ser=VendorModelSer(data=request.data,instance=vendor)
            if ser.is_valid():
                ser.save()
                return Response({"msg":"Vendor Details Updated"},status=status.HTTP_202_ACCEPTED)
        except Vendor.DoesNotExist:
            return Response({"msg": f"Vendor with ID {vid} not found"}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({"msg": "Failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Delete a vendor.
    def destroy(self,request,*args,**kwargs):
        vid=kwargs.get('pk')
        try:
            vendor=Vendor.objects.get(id=vid)
            vendor.delete()
            return Response({"msg":"Deleted"},status=status.HTTP_200_OK)
        except Vendor.DoesNotExist:
            return Response({"msg": f"Vendor with ID {vid} not found"}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({"msg": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    #  Retrieves the calculated performance metrics for a specific vendor
    @action(methods=['GET'],detail=True)
    def performance(self,request,*args,**kwargs):
        vid=kwargs.get('pk')
        try:
            vendor_ob=Vendor.objects.get(id=vid)
            try:
                performance=HistoricalPerformance.objects.get(vendor=vendor_ob)
                dser=PerformanceModelSer(performance)
                return Response(dser.data,status=status.HTTP_200_OK)
            except HistoricalPerformance.DoesNotExist:
                return Response({"msg": f"Historical Performance with the vendor {vendor_ob.name} not found"}, status=status.HTTP_404_NOT_FOUND)
        
        except Vendor.DoesNotExist:
                return Response({"msg": f"Vendor with ID {vid} not found"}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({"msg": "Failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# Purchase Order viewset
class PurchaseOrderViewSet(ViewSet):     
    authentication_classes=[TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]

    # Create a new Purchase Order.
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'vendor': openapi.Schema(type=openapi.TYPE_INTEGER),
                'order_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                'delivery_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                'items': openapi.Schema(type=openapi.TYPE_STRING, format='json'),
                'quantity': openapi.Schema(type=openapi.TYPE_INTEGER),
                'status': openapi.Schema(type=openapi.TYPE_STRING),
                'quality_rating': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT),
                'issue_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                'acknowledgment_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                 },
            required=['vendor', 'order_date', 'delivery_date','items','quantity','status','issue_date'],
                    ),
        responses={201: "Your Response Description"},
    )
    def create(self, request, *args, **kwargs):
        ser = PurchaseOrderModelSer(data=request.data)
        try:
            if ser.is_valid():
                ser.save()
                return Response({"msg": "Purchase order created"}, status=status.HTTP_201_CREATED)
            return Response({"msg":ser.errors},status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response({"msg": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    
    # List all Purchase Order for corresponding vendor.
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'vendor_id',
                openapi.IN_QUERY,
                description="Filter purchase orders by vendor ID",
                type=openapi.TYPE_INTEGER,
                required= False,
            ),
        ],
        responses={200: PurchaseOrderModelSer(many=True)},
    )
    def list(self,request):
        po_queryset=PurchaseOrder.objects.all()
        try:
            if 'vendor_id' in request.query_params:
                vendor_id=request.query_params.get('vendor_id')

                try:
                    vendor_ob=Vendor.objects.get(id=vendor_id)
                    po_queryset=po_queryset.filter(vendor=vendor_ob)
                    dser=PurchaseOrderModelSer(po_queryset,many=True)
                    return Response(data=dser.data)
                except:
                    return Response({"msg":"Invalid Vendor Id passed in query parameter"})
                
            else:
                po_queryset=PurchaseOrder.objects.all()
                dser=PurchaseOrderModelSer(po_queryset,many=True)
                return Response(data=dser.data)
        except:
            return Response({"msg":"Failed"},status=status.HTTP_404_NOT_FOUND)
    

    # Retrieve a specific purchase order details.
    def retrieve(self,request,*args,**kwargs):
        po_id=kwargs.get('pk')
        try:
            purchase_order=PurchaseOrder.objects.get(id=po_id)
            dser=PurchaseOrderModelSer(purchase_order)
            return Response(data=dser.data)
        except PurchaseOrder.DoesNotExist:
            return Response({"msg": f"Purchase Order with ID {po_id} not found"}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({"msg": "Failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

    # Update a specific purchase order details.
    @swagger_auto_schema(request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'vendor': openapi.Schema(type=openapi.TYPE_INTEGER),
                'order_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                'delivery_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                'items': openapi.Schema(type=openapi.TYPE_STRING, format='json'),
                'quantity': openapi.Schema(type=openapi.TYPE_INTEGER),
                'status': openapi.Schema(type=openapi.TYPE_STRING),
                'quality_rating': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT),
                'issue_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                'acknowledgment_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                 },
            required=['vendor', 'order_date', 'delivery_date','items','quantity','status','issue_date'],
                    ),
        responses={201: "Your Response Description"},)
    def update(self,request,*args,**kwargs):
        po_id=kwargs.get('pk')
        print(po_id)
        try:
            purchase_order=PurchaseOrder.objects.get(id=po_id)
            print(purchase_order)
            ser=PurchaseOrderModelSer(data=request.data,instance=purchase_order,partial=True)
            if ser.is_valid():
                ser.save()
                return Response({"message":"Purchase order Details Updated"},status=status.HTTP_202_ACCEPTED)
            return Response({"msg":ser.errors},status=status.HTTP_400_BAD_REQUEST)
        
        except PurchaseOrder.DoesNotExist:
            return Response({"msg": f"Purchase Order with ID {po_id} not found"}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({"msg": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    # Delete a specific purchase order details.
    def destroy(self,request,*args,**kwargs):
        po_id=kwargs.get('pk')
        try:
            purchase_order=PurchaseOrder.objects.get(id=po_id)
            purchase_order.delete()
            return Response({"msg":"Deleted"},status= status.HTTP_200_OK)
        
        except PurchaseOrder.DoesNotExist:
            return Response({"msg": f"Purchase Order with ID {po_id} not found"}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({"msg": "Failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    #   update acknowledgment_date and trigger the recalculation of average_response_time.  
    @swagger_auto_schema(request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'acknowledgment_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                 },
            required=['acknowledgment_date'],
                    ),
        responses={201: "Your Response Description"},)
    @action(methods=['POST'], detail=True)
    def acknowledge(self, request, *args, **kwargs):
        po_id = kwargs.get('pk')
        try:
            purchase_order = PurchaseOrder.objects.get(id=po_id)
            ser = AcknowledgeModelSer(data=request.data, instance=purchase_order)

            if ser.is_valid():
                # purchase_order.acknowledgment_date = ser.validated_data.get('acknowledgment_date')
                # purchase_order.save()
                ser.save()
                return Response({"message": "Purchase order acknowledge date is Updated"},status=status.HTTP_202_ACCEPTED)
            return Response({"msg": ser.errors})
        
        except PurchaseOrder.DoesNotExist:
            return Response({"msg": f"Purchase Order with ID {po_id} not found"}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({"msg": "Failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

