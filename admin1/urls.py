from django.urls import path
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.routers import DefaultRouter
from admin1 import views

router=DefaultRouter()

router.register("vendors",views.VendorView,basename="vendor_list")
router.register("customers",views.CustomerView,basename="cust_list")
router.register("orders",views.OrdersView,basename="orders_list")


urlpatterns = [
    path('token/',views.CustomAuthToken.as_view(), name='token'),

    
] +router.urls

