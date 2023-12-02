from django.test import TestCase
from django.db.models.signals import post_save,pre_save,post_delete
from vendor.signals import *

class YourTestCase(TestCase):
    def setUp(self):
        # Disconnect the signal receiver during tests
        pre_save.connect(capture_previous_status, sender=PurchaseOrder)
        post_save.connect(handle_po_update, sender=PurchaseOrder)
        post_delete.connect(handle_po_delete, sender=PurchaseOrder)
        # Additional setup code

    def tearDown(self):
        pre_save.disconnect(capture_previous_status, sender=PurchaseOrder)
        post_save.disconnect(handle_po_update, sender=PurchaseOrder)
        post_delete.disconnect(handle_po_update, sender=PurchaseOrder)
    #     # Reconnect the signal receiver after tests
