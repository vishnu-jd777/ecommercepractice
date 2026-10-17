from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from . models import User, Address
# Register your models here.
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (('Extra', {'fields': ('phone',)}),)

admin.site.register(User, CustomUserAdmin)
admin.site.register(Address)