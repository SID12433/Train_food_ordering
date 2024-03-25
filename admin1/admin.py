from django.contrib import admin
from admin1.models import Category,Food,Vendor,Customer,Cart,CartItem,Review,Order,CustomUser
# Register your models here.

admin.site.register(Vendor)
admin.site.register(Customer)
admin.site.register(CustomUser)