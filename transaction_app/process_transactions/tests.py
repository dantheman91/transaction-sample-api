from django.test import TestCase
from rest_framework.test import APIRequestFactory

from .models import Item, Transaction
from .views import CreateItem, CreateTransaction


# Create your tests here.
class BaseIntegrationTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        # Setup an item to be used in creating and moving transactions
        data = {'amount': '20.00'}
        request = self.factory.post('/create_item/', data)
        response = CreateItem.as_view()(request)
        self.item_id = response.data["item_id"]

    def test_failed_create_item_with_inaccurate_key(self):
        data = {'asdf': '9.00'}
        request = self.factory.post('/create_item/', data)
        response = CreateItem.as_view()(request)
        print('test_1')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {'amount': ['This field is required.']})

    def test_create_item(self):
        data = {'amount': '9.00'}
        print('test_2')
        request = self.factory.post('/create_item/', data)
        response = CreateItem.as_view()(request)
        self.assertEqual(response.data["amount"], "9.00")
        self.assertEqual(response.status_code, 201)

    def test_create_transaction(self):
        data = {
            'item_id': self.item_id
        }
        request = self.factory.post('/create_transaction/', data)
        response = CreateTransaction.as_view()(request)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["status"], "processing")
        self.assertEqual(response.data["location"], "origination_bank")


