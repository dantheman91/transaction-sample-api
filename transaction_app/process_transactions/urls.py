from django.urls import path
from . import views

urlpatterns = [
    path('create_item/', views.CreateItem.as_view()),
    path('create_transaction/', views.CreateTransaction.as_view()),
    path('move_item/', views.MoveItem.as_view()),
    path('error_item/', views.MoveItem.as_view()),
]
