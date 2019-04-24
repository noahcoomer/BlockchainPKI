from django.urls import path
from . import views
urlpatterns = [
    path('', views.index),
    path('transaction',views.TransactionView, name="transaction"),
    path('block',views.BlockView, name ="block")
]
