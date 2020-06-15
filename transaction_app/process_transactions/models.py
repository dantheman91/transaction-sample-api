import uuid
from django.db import models


# An item in this case is analogous to a payment
class Item(models.Model):
    item_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    amount = models.DecimalField(decimal_places=2, max_digits=15)


# This class is used to process multiple transactions for an item
class Transaction(models.Model):
    transaction_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item_id = models.ForeignKey('Item', on_delete=models.CASCADE)
    status = models.CharField(max_length=128)
    location = models.CharField(max_length=1024)


class ItemLog(models.Model):
    request_and_response_body = models.TextField()
