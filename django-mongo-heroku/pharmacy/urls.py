
#from django.contrib import admin
from django.urls import path
from pharmacy import views as pharmacy_views

urlpatterns = [

    path('orders/', pharmacy_views.orders, name='orders')
    path('fetch_all_orders_data/', pharmacy_views.fetch_all_orders_data, name='fetch_all_orders_data'),
]
