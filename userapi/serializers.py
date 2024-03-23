from admin1.models import Customer,Food,Review,Order,Cart,CartItem,Category,Vendor,RestaurantReview
from rest_framework import serializers

class CustomerSerializer(serializers.ModelSerializer):
    id=serializers.CharField(read_only=True)
    password=serializers.CharField(write_only=True)

    class Meta:
        model=Customer
        fields=["id","name","phone","username","date_of_birth","profile_picture","bio","address","password"]

    def create(self, validated_data):
        return Customer.objects.create_user(**validated_data)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model=Category
        fields="__all__"
        
class RestaurantReviewSerializer(serializers.ModelSerializer):
    user=serializers.CharField(read_only=True)
    class Meta:
        model=RestaurantReview
        fields=["user","vendor","rating","comment"]

class VendorSerializer(serializers.ModelSerializer):
    restaurantreview=RestaurantReviewSerializer(many=True,read_only=True)
    class Meta:
        model=Vendor
        fields=["id","name","description","address","logo","website","restaurantreview"]
        
class FoodSerializer(serializers.ModelSerializer):
    class Meta:
        model=Food
        fields="__all__"
        
class CartItemsSerializer(serializers.ModelSerializer):
    food=FoodSerializer(read_only=True)
    class Meta:
        model=CartItem
        fields="__all__"
        read_only_fields=["cart","food","created_at","updated_at"]
        
class CartSerializer(serializers.ModelSerializer):
    cartitems=CartItemsSerializer(many=True,read_only=True)
    cart_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)    
    class Meta:
        model=Cart
        fields=["id","cartitems","user","cart_total","status","created_at","updated_at","is_active"]
        
        
        
class OrderSerializer(serializers.ModelSerializer):
    cart=serializers.CharField(read_only=True)
    status=serializers.CharField(read_only=True)
    orderd_date=serializers.CharField(read_only=True)
    expected_date=serializers.CharField(read_only=True)
    class Meta:
        model=Order
        fields=["cart","train_no","seatno","coach_no","orderd_date","expected_date","status","razorpay_order_id","order_amount"]

class ReviewSerializer(serializers.ModelSerializer):
    user=serializers.CharField(read_only=True)
    class Meta:
        model=Review
        fields=["user","food","rating","comment"]
        
        

