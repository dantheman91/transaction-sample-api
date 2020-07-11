from django.test import TestCase
from rest_framework.test import APIRequestFactory

from .models import Item, Transaction
from .views import CreateItem, CreateTransaction, MoveItem


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
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {'amount': ['This field is required.']})

    def test_create_item(self):
        data = {'amount': '9.00'}
        request = self.factory.post('/create_item/', data)
        response = CreateItem.as_view()(request)
        self.assertEqual(response.data["amount"], "9.00")
        self.assertEqual(response.status_code, 201)

    def test_create_transaction_and_move_item(self):
        invalid_create_data = {
            'item_id': self.item_id,
        }
        request = self.factory.post('/create_transaction/', invalid_create_data)
        response = CreateTransaction.as_view()(request)
        self.assertEqual(response.status_code, 400)
        valid_create_data = {
            'item_id': self.item_id,
            'destination': 'test_bank'
        }
        request = self.factory.post('/create_transaction/', valid_create_data)
        response = CreateTransaction.as_view()(request)
        self.assertEqual(response.status_code, 201)
        valid_move_data = {
            'item_id': self.item_id,
        }
        request = self.factory.post('/error_item/', valid_move_data)
        response = MoveItem.as_view()(request)
        self.assertEqual(response.status_code, 400)
        request = self.factory.post('/move_item/', valid_move_data)
        response = MoveItem.as_view()(request)
        self.assertEqual(response.status_code, 202)
        request = self.factory.post('/error_item/', valid_move_data)
        response = MoveItem.as_view()(request)
        self.assertEqual(response.status_code, 202)
        request = self.factory.post('/move_item/', valid_move_data)
        response = MoveItem.as_view()(request)
        self.assertEqual(response.status_code, 400)
        request = self.factory.post('/create_transaction/', valid_create_data)
        response = CreateTransaction.as_view()(request)
        self.assertEqual(response.status_code, 201)
        request = self.factory.post('/move_item/', valid_move_data)
        response = MoveItem.as_view()(request)
        self.assertEqual(response.status_code, 202)
        request = self.factory.post('/move_item/', valid_move_data)
        response = MoveItem.as_view()(request)
        self.assertEqual(response.status_code, 202)
        request = self.factory.post('/move_item/', valid_move_data)
        response = MoveItem.as_view()(request)
        self.assertEqual(response.status_code, 400)
