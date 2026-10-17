from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/',views.register_view,name='signup'),
    path('login/',auth_views.LoginView.as_view(template_name='accounts_templates/login.html'),name='login'),
    path('logout/',auth_views.LogoutView.as_view(),name='logout'),
    path('profile/',views.profile_view,name='profile'),
    path('profile/edit',views.edit_profile_view,name='edit_profile'),
    path('addresses/',views.address_list_view,name='address_list'),
    path('addresses/add',views.add_address_view,name='add_address'),
    path('addresses/<int:pk>/edit/',views.edit_address_view,name='edit_address'),
    path('addresses/<int:pk>/delete/',views.delete_address_view,name='delete_address'),



]