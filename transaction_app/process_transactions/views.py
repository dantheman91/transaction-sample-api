import django.core.exceptions as django_exceptions
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Item, Transaction, ItemLog
from .serializers import ItemSerializer, TransactionSerializer

class ParentAPIView(APIView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.request_and_response_logs = []

    def pre_request(self, request):
        self.logging_setup()
        self.add_to_logging({
            'request': {
                'request_data': request.data,
                'request_path': request.get_full_path()
                }
            })

    def post_request(self, response, http_code):
        self.add_to_logging({
            'response': response,
            'http_code': http_code
        })
        log = ItemLog(request_and_response_body=self.request_and_response_logs)
        try:
            log.save()
        except Exception as e:
            print('Unable to save to database')
            print(e)

    def add_to_logging(self, logging_object):
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
        print(request.data)
        request_data = request.data
        request_data["status"] = "processing"
        request_data["location"] = "origination_bank"
        serializer = TransactionSerializer(data=request_data)
        if serializer.is_valid() and serializer.validate_no_active_transactions(request_data["item_id"]):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AbstractMoveItem(ParentAPIView):

    def __init__(self):
        self.response_data = {}
        self.transaction = {}

    # This is where we store our locations movement data structure
    # I.e.
    # {
    # 	"initial_status": ("routable", "processing"),
    # 	"moved_status": ("destination_bank", "completed")
    # }
    location_hierarchy = {}

    def post(self, request, format=None):
        request_data = request.data
        if request_data.get('transaction_id') is None:
            return Response({'Error': 'transaction_id missing'}, status=status.HTTP_400_BAD_REQUEST)
        if self.transaction_completed_or_missing(request.data['transaction_id']):
            return Response(self.response_data, status=status.HTTP_400_BAD_REQUEST)
        else:
            self.transaction.location = self.location_hierarchy[self.transaction.location]
            if self.transaction.location == "destination_bank":
                self.transaction.status = "completed"
            self.transaction.save()
            self.response_data = {'transaction_id': self.transaction.transaction_id,
                                  'location': self.transaction.location,
                                  'status': self.transaction.status}
        return Response(self.response_data, status=status.HTTP_202_ACCEPTED)

    def transaction_completed_or_missing(self, transaction_id):
        return_value = False
        try:
            self.transaction = Transaction.objects.get(transaction_id=transaction_id)
            if self.transaction.status == 'completed' or self.transaction.status == 'error':
                self.response_data['error'] = f'Transaction: {transaction_id} Status: {self.transaction.status}.'
                return_value = True
        except django_exceptions.ObjectDoesNotExist:
            self.response_data['error'] = f'Transaction: {transaction_id} not found.'
            return_value = True
        return return_value


class ErrorItem(ParentAPIView):

    def __init__(self):
        self.response_data = {}
        self.transaction = {}

    location_hierarchy = {
        "origination_bank": "routable",
        "routable": "destination_bank"
    }

    def post(self, request, format=None):
        request_data = request.data
        if request_data.get('transaction_id') is None:
            return Response({'Error': 'transaction_id missing'}, status=status.HTTP_400_BAD_REQUEST)
        if self.transaction_processing_and_in_routable(request.data['transaction_id']) is not True:
            return Response(self.response_data, status=status.HTTP_400_BAD_REQUEST)
        else:
            self.transaction.status = "error"
            self.transaction.save()
            self.response_data = {'transaction_id': self.transaction.transaction_id,
                                  'location': self.transaction.location,
                                  'status': self.transaction.status}
        return Response(self.response_data, status=status.HTTP_202_ACCEPTED)

    def transaction_processing_and_in_routable(self, transaction_id):
        return_value = False
        try:
            self.transaction = Transaction.objects.get(transaction_id=transaction_id)
            if self.transaction.status == 'processing' and self.transaction.location == 'routable':
                pass
            else:
                self.response_data['error'] = f'Transaction: {transaction_id} Status: {self.transaction.status}.'
                return_value = True
        except django_exceptions.ObjectDoesNotExist:
            self.response_data['error'] = f'Transaction: {transaction_id} not found.'
            return_value = True
        return return_value