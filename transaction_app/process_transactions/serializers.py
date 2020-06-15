import json

from rest_framework import serializers
from .models import Item, Transaction


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['item_id', 'amount']


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['transaction_id', 'item_id', 'status', 'location']

    @staticmethod
    def validate_no_active_transactions(item_id):
        """
        Check that the item_id doesn't already have a processing transaction
        """
        transaction_already_processing = Transaction.objects.filter(item_id=item_id, status="processing").values('transaction_id', 'location')
        print(transaction_already_processing)
        if len(transaction_already_processing) > 0:
            raise serializers.ValidationError(f"There is already a transaction that is being processed: {transaction_already_processing[0]}")
        return True
