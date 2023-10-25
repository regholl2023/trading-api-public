from django.urls import path
from . import views

urlpatterns = [
    path('get-url/', views.place_order, name='get-url'),
    path('place-order/', views.place_order, name='place-order'),
    path('close-trades/', views.close_trades, name='close-trades'),
    path('get-balances/', views.get_balances, name='get-balances'),
]
