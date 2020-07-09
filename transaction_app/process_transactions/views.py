import django.core.exceptions as django_exceptions
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Item, Transaction, ItemLog
from .serializers import ItemSerializer, TransactionSerializer
from .logger import APILogger


class ParentAPIView(APIView):

    def __init__(self):
        self.logger = APILogger()

    def complete_response(self, data, status):
        self.logger.log_response(data, status)
        return Response(data, status=status)


class CreateItem(ParentAPIView):
    def post(self, request, format=None):
        self.logger.add_to_logging(request.data)
        serializer = ItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return self.complete_response(serializer.data, status.HTTP_201_CREATED)
        return self.complete_response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class CreateTransaction(ParentAPIView):
    def post(self, request, format=None):
        request_data = request.data
        self.logger.add_to_logging(request_data)
        request_data["status"] = "processing"
        request_data["location_id"] = settings.ORIGINATION_BANK
        serializer = TransactionSerializer(data=request_data)
        if serializer.is_valid() and serializer.validate_no_active_or_completed_transactions(request_data["item_id"]):
            serializer.save()
            serializer_data = serializer.data
            serializer_data['location'] = settings.PROCESSING_STATE[serializer_data['location_id']]
            del serializer_data['location_id']
            return self.complete_response(serializer_data, status=status.HTTP_201_CREATED)
        return self.complete_response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MoveItem(ParentAPIView):

    def __init__(self):
        super().__init__()
        self.response_data = {}
        # This is where we store our locations movement data structure
        # I.e.
        # {
        # 	"initial_status": ("routable", "processing"),
        # 	"moved_status": ("destination_bank", "completed")
        # }
        self.location_hierarchy = {}

    def post(self, request, format=None):
        http_return_code = status.HTTP_202_ACCEPTED
        self.logger.log_request(request)
        request_data = request.data
        self.set_location_hierarchy(request.get_full_path())
        if request_data.get('item_id') is None:
            self.response_data['error'] = 'Item_id missing'
            http_return_code = status.HTTP_400_BAD_REQUEST
        else:
            if self.move_item(request_data.get('item_id')):
                pass
            else:
                http_return_code = status.HTTP_400_BAD_REQUEST
        return self.complete_response(self.response_data, status=http_return_code)

    def move_item(self, item_id):
        return_value = False
        try:
            transactions = Transaction.objects.filter(item_id=item_id)
        except django_exceptions.ObjectDoesNotExist:
            self.response_data['error'] = f'Transaction for: {item_id} not found. Please create a transaction'
        matching_transaction_found_and_updated = self.update_transaction(transactions)
        if matching_transaction_found_and_updated is False:
            self.response_data['error'] = f'Unable to move item: {item_id}. Please try creating a new transaction, or' \
                                          f' the transaction is complete and a new item must be created.'
        else:
            return_value = True
        return return_value

    def set_location_hierarchy(self, full_path):
        if full_path == '/move_item/':
            self.location_hierarchy = [{
                    "initial_status": (settings.ORIGINATION_BANK, "processing"),
                    "moved_status": (settings.ROUTABLE, "processing")
                },
                {
                    "initial_status": (settings.ROUTABLE, "processing"),
                    "moved_status": (settings.DESTINATION_BANK, "completed")
                },
            ]
        elif full_path == '/error_item/':
            self.location_hierarchy = [{
                "initial_status": (settings.ROUTABLE, "processing"),
                "moved_status": (settings.ROUTABLE, "error")
            }
            ]

    def update_transaction(self, transactions):
        for transaction in transactions:
            for location in self.location_hierarchy:
                if (transaction.location_id, transaction.status) == location["initial_status"]:
                    transaction.location_id, transaction.status = location["moved_status"]
                    try:
                        transaction.save()
                        self.response_data = {
                            'item_id': transaction.item_id.item_id,
                            'location': settings.PROCESSING_STATE[transaction.location_id],
                            'status': transaction.status
                        }
                    except Exception as e:
                        self.response_data['error'] = f'Unable to complete transaction: {transaction.transaction_id}.' \
                                                      f'Current location: {settings.PROCESSING_STATE[transaction.location_id]}' \
                                                      f'Current status: {transaction.status}'
                    return True
        return False
