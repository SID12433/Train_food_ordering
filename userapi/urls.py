from django.urls import path
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.routers import DefaultRouter
from userapi import views

router=DefaultRouter()
router.register("category",views.CategoryView,basename="category")
router.register("vendors",views.VendorView,basename="vendor_list")
router.register("food",views.FoodView,basename="food")
router.register("cart",views.CartView,basename="cart_list")


urlpatterns = [
    path("register/",views.CustomerCreationView.as_view(),name="signup"),
    path("token/",ObtainAuthToken.as_view(),name="token"),
    path("logout/",views.sign_out,name="logout"),

    
] +router.urls

