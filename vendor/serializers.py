from rest_framework import serializers
from admin1.models import Category,Food,Cart,Offer,Order,Review,Vendor,Customer,CartItem
# from django.contrib.auth.models import User



class VendorSerializer(serializers.ModelSerializer):
    id=serializers.CharField(read_only=True)
    password=serializers.CharField(write_only=True)

    class Meta:
        model=Vendor
        fields=["id","username","email","password","phone","name","description","address","website","logo"]
    # def create(self, validated_data):
    #     user = UserSignup(
    #         email=validated_data['email'],
    #         username=validated_data['username']
    #     )
    #     user.set_password(validated_data['password'])
    #     user.save()
    #     return user
    def create(self, validated_data):
        return Vendor.objects.create_user(**validated_data)
    
class CategorySerializer(serializers.ModelSerializer):
    id=serializers.CharField(read_only=True)
    is_active=serializers.BooleanField(read_only=True)
    class Meta:
        model = Category
        fields =["id","name","is_active"]
        
class OfferSerializer(serializers.ModelSerializer):
    food=serializers.CharField(read_only=True)
    id=serializers.CharField(read_only=True)
    status=serializers.CharField(read_only=True)
    vendors=serializers.CharField(read_only=True)
    class Meta:
        model = Offer
        fields="__all__"


class FoodSerializer(serializers.ModelSerializer):
    id=serializers.CharField(read_only=True)
    category=serializers.CharField(read_only=True)
    is_active=serializers.BooleanField(read_only=True)
    class Meta:
        model = Food
        fields = ["id","name","description","price","image","is_active","category"]
        
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model=Review
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
    id = serializers.CharField(read_only=True)
    food_items = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = "__all__"
    
    def get_food_items(self, obj):
        return [item.food.name for item in obj.cart.cartitem.all()] if obj.cart else []



        
    




