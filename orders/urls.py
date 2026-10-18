from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout_view, name='checkout'),
    path(
        'success/<int:order_id>/',
        views.order_success_view,
        name='order_success'
    ),

    path('', views.order_list_view, name='order_list'),
    path('<int:order_id>/', views.order_detail_view, name='order_detail'),
    path('<int:order_id>/cancel/', views.cancel_order_view, name='cancel_order'),
]