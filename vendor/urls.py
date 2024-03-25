from django.urls import path
from vendor import views
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.routers import DefaultRouter

router=DefaultRouter()
router.register("foods",views.FoodView,basename="foods")
router.register("offers",views.OfferView,basename="offers")
router.register("category",views.CategoryView,basename="category")
router.register("orders",views.OrderView,basename="order-list")
router.register("profile",views.ProfileView,basename="profile")

urlpatterns=[
    path("register/",views.VendorCreationView.as_view(),name="signin"),
    path('token/',views.CustomAuthToken.as_view(), name='token'),
    
    
    
  
    
]+router.urls


