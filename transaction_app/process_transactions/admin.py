from django.contrib import admin

from .models import Item, ItemLog, Transaction

# Register your models here.
admin.site.register(Item)
admin.site.register(ItemLog)
admin.site.register(Transaction)
