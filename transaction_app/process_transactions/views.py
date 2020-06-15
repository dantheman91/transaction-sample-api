import django.core.exceptions as django_exceptions
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Item, Transaction, ItemLog
from .serializers import ItemSerializer, TransactionSerializer


class ParentAPIView(APIView):

    def __init__(self):
        request_and_response_logs = []

    def pre_request(self, request):
        self.add_to_logging({
            'request': {
                'request_data': request.data,
                'request_path': request.get_full_path()
                }
            })

    def log_response(self, http_code):
        self.add_to_logging({
            'response': self.response_data,
            'http_code': http_code
        })
        log = ItemLog(request_and_response_body=self.request_and_response_logs)
        try:
            log.save()
        except Exception as e:
            print('Unable to save to database')
            print(e)

    def add_to_logging(self, logging_object):
        print(logging_object)
        print(self.request_and_response_logs)
        self.request_and_response_logs.append(logging_object)


class CreateItem(ParentAPIView):
    def post(self, request, format=None):
        serializer = ItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateTransaction(ParentAPIView):
    def post(self, request, format=None):
        request_data = request.data
        request_data["status"] = "processing"
        request_data["location"] = "origination_bank"
        serializer = TransactionSerializer(data=request_data)
        if serializer.is_valid() and serializer.validate_no_active_transactions(request_data["item_id"]):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
        self.pre_request(request)
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
        self.log_response(http_return_code)
        return Response(self.response_data, status=http_return_code)

    def move_item(self, item_id):
        return_value = False
        try:
            transactions = Transaction.objects.filter(item_id=item_id)
        except django_exceptions.ObjectDoesNotExist:
            self.response_data['error'] = f'Item: {item_id} not found.'
        matching_transaction_found_and_updated = self.update_transaction(transactions)

        if matching_transaction_found_and_updated is False:
            self.response_data['error'] = f'Unable to move item: {item_id}.'
        else:
            return_value = True
        return return_value

    def set_location_hierarchy(self, full_path):
        if full_path == '/move_item/':
            self.location_hierarchy = [{
                    "initial_status": ("origination_bank", "processing"),
                    "moved_status": ("routable", "processing")
                },
                {
                    "initial_status": ("routable", "processing"),
                    "moved_status": ("destination_bank", "completed")
                },
            ]
        elif full_path == '/error_item/':
            self.location_hierarchy = [{
                "initial_status": ("routable", "processing"),
                "moved_status": ("routable", "error")
            }
            ]

    def update_transaction(self, transactions):
        for transaction in transactions:
            for location in self.location_hierarchy:
                if (transaction.location, transaction.status) == location["initial_status"]:
                    transaction.location, transaction.status = location["moved_status"]
                    try:
                        transaction.save()
                    except Exception as e:
                        self.response_data['error'] = f'Unable to save transactions: {transaction.transaction_id}.'
                    self.response_data = {'item_id': transaction.item_id.item_id,
                                          'location': transaction.location,
                                          'status': transaction.status}
                    return True
        return False
