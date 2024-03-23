from django.urls import path
from vendor import views
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.routers import DefaultRouter

router=DefaultRouter()
router.register("foods",views.FoodView,basename="foods")
router.register("offers",views.OfferView,basename="offers")
router.register("category",views.CategoryView,basename="category")
router.register("orders",views.OrderView,basename="order-list")
# router.register("reviews",views.ReviewView,basename="review")

urlpatterns=[
    path("register/",views.VendorCreationView.as_view(),name="signin"),
    path("token/",ObtainAuthToken.as_view(),name="token"),
    path("logout/",views.sign_out,name="logout"),
    
    
    
  
    
]+router.urls


