from admin1.models import Customer,Food,Review,Order,Cart,CartItem,Category,Vendor,RestaurantReview,Offer
from rest_framework import serializers


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields ="__all__"
        
        
class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields ="__all__"
        
        
        
class OfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields="__all__"


class FoodSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    category = serializers.CharField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    offer = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()

    class Meta:
        model = Food
        fields = ["id", "name", "description", "price", "image", "is_active", "category", "type", "offer","reviews"]

    def get_offer(self, obj):
        vendor = obj.vendor
        offer = Offer.objects.filter(food=obj, vendors=vendor).first()
        if offer:
            return {
                'price': offer.price,
                'start_date': offer.start_date,
                'due_date': offer.due_date,
                'offer_status': offer.offer_status
            }
        return None
    
    def get_reviews(self, obj):
        reviews = Review.objects.filter(food=obj)
        return ReviewSerializer(reviews, many=True).data
    
    
class ReviewSerializer(serializers.ModelSerializer):
    user=CustomerSerializer()
    food=FoodSerializer()
    
    class Meta:
        model=Review
        fields=["id","user","food","rating","comment"]
        
        
class RestaurantReviewSerializer(serializers.ModelSerializer):
    user=CustomerSerializer()
    vendor=VendorSerializer()
    
    class Meta:
        model = RestaurantReview
        fields="__all__"    
        
        
        

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model=Cart
        fields=["cartitems","user"]    
        
        
class OrderSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    cart=CartSerializer()
    food_items = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = "__all__"
    
    def get_food_items(self, obj):
        return [item.food.name for item in obj.cart.cartitem.all()] if obj.cart else []