from django.urls import path
from . import views 

app_name = 'store'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('products/', views.product_list_view, name='product_list'),
    path('category/<slug:slug>/', views.category_view, name='category'),
    path('product/<slug:slug>/', views.product_detail_view, name='product_detail'),
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/toggle/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),
    path('product/<slug:slug>/review/', views.add_review, name='add_review'),
    path('review/<int:review_id>/delete/', views.delete_review, name='delete_review'),
]