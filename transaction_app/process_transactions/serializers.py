import json

from django.db.models import CharField
from django.db.models.functions import Cast
from rest_framework import serializers

from .models import Item, Transaction


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['item_id', 'amount']


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['transaction_id', 'item_id', 'destination', 'location_id', 'status']

    @staticmethod
    def validate_no_active_or_completed_transactions(item_id):
        """
        Check that the item_id doesn't already have a processing transaction
        """
        transaction_already_processing = Transaction.objects.filter(
            item_id=item_id, status__in=("processing", "completed")).values(transaction=Cast(
                                                                            'transaction_id', output_field=CharField()))
        if transaction_already_processing:
            transaction_id = transaction_already_processing[0]
            raise serializers.ValidationError(
                f"There is already a transaction that is being "
                f"processed or already completed: {transaction_id}")
        return True
