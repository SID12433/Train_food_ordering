from django.db import models
# from django.contrib.gis.db import models
import requests

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db.models.signals import post_save
from django.contrib.auth.models import User

class CustomUser(AbstractUser):
    user_type_choices=[
        ('customer', 'customer'),
        ('vendor' ,'vendor'),
    ]
    user_type=models.CharField(max_length=50,choices=user_type_choices,default='customer')
    phone=models.CharField(max_length=10)



class Vendor(CustomUser):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=200,null=True)
    address = models.CharField(max_length=200,null=True)
    website = models.URLField(null=True)
    logo = models.ImageField(upload_to='images',null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    @property
    def restaurantreview(self):
        qs=self.restaurant_review.all()
        return qs
   
    
class Customer(CustomUser):
    name=models.CharField(max_length=50)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='images', null=True)
    bio = models.TextField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    # location = models.PointField(blank=True, null=True)

    def __str__(self):
        return self.name
    

    # def save(self, *args, **kwargs):
    #     if not self.location:
    #         self.location = self.geocode_address(self.address)
    #     super().save(*args, **kwargs)

    # def geocode_address(self, address):
    #     api_key = 'YOUR_GOOGLE_MAPS_API_KEY'
    #     base_url = 'https://maps.googleapis.com/maps/api/geocode/json'
    #     params = {'address': address, 'key': api_key}
    #     response = requests.get(base_url, params=params)
    #     data = response.json()

    #     if data['status'] == 'OK':
    #         location = data['results'][0]['geometry']['location']
    #         return Point(location['lng'], location['lat'])
    #     else:
    #         return None
   


class Category(models.Model):
    name=models.CharField(max_length=200)
    vendors = models.ForeignKey(Vendor,on_delete=models.CASCADE)
    is_active=models.BooleanField(default=True)

    def __str__(self):
        return self.name

        
    
class Food(models.Model):
    name=models.CharField(max_length=200)
    vendor=models.ForeignKey(Vendor,on_delete=models.CASCADE,null=True)
    category=models.ForeignKey(Category,on_delete=models.CASCADE)
    image=models.ImageField(upload_to="images")
    price=models.PositiveIntegerField()
    description=models.CharField(max_length=500)
    is_active=models.BooleanField(default=True)

    def __str__(self):
        return self.name
    

    
    
class Offer(models.Model):
    food=models.ForeignKey(Food,on_delete=models.CASCADE,related_name="offer_price")
    vendors = models.ForeignKey(Vendor,on_delete=models.CASCADE)
    price=models.PositiveIntegerField()
    start_date=models.DateTimeField()
    due_date=models.DateTimeField()
    options=(
        ("active","active"),
        ("expired","expired")
    )
    offer_status=models.CharField(max_length=200,choices=options,default="active")
    
    
    @property
    def status(self):
        return "expired" if self.due_date < timezone.now() else "active"
    
    
class Cart(models.Model):
    user=models.OneToOneField(Customer,on_delete=models.CASCADE,related_name="cart")
    options=(
        ("in-cart","in-cart"),
        ("order-placed","order-placed"),
        ("cancelled","cancelled")
    )

    status=models.CharField(max_length=200,choices=options,default="in-cart")
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    is_active=models.BooleanField(default=True)
    
    @property
    def cartitems(self):
        qs=self.cartitem.all()
        return qs
    
    @property
    def calculate_total_amount(self):
        total_amount = sum(item.total_amount for item in self.cartitem.all())
        return total_amount
    
    @property
    def cart_total(self):
        qs=self.calculate_total_amount
        return qs
    


class CartItem(models.Model):
    cart=models.ForeignKey(Cart,on_delete=models.CASCADE,related_name="cartitem") 
    food=models.ForeignKey(Food,on_delete=models.CASCADE)
    quantity=models.PositiveIntegerField(default=1)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    is_active=models.BooleanField(default=True)
    
    @property
    def total_amount(self):
        if self.is_active_offer():
            return self.quantity * self.food.price - self.get_offer_price()
        else:
            return self.quantity * self.food.price

    def is_active_offer(self):
        active_offer = Offer.objects.filter(food=self.food,offer_status="active").first()
        return active_offer is not None

    def get_offer_price(self):
        active_offer = Offer.objects.filter(food=self.food,offer_status="active").first()
        return active_offer.price if active_offer else 0
        
    



class Order(models.Model):
    user=models.ForeignKey(Customer,on_delete=models.CASCADE)
    train_no=models.CharField(max_length=100)
    cart=models.ForeignKey(Cart,on_delete=models.CASCADE,null=True)
    options=(
      
        ("order-placed","order-placed"),
        ("cancelled","cancelled"),
        ("dispatced","dispatched"),
        ("in-transit","in-transit"),
        ("delivered","delivered")
    )
    status=models.CharField(max_length=200,choices=options,default="order-placed")
    orderd_date=models.DateTimeField(auto_now_add=True)
    coach_no=models.CharField(max_length=100)
    seatno=models.CharField(max_length=100,unique=True)
    order_amount = models.CharField(max_length=100,null=True,blank=True)
    razorpay_order_id = models.CharField(max_length=255, null=True, blank=True)
    
    @property
    def food_items(self):
        if self.cart:
            return [item.food for item in self.cart.cartitem_set.all()]
        return []



from django.core.validators import MinValueValidator,MaxValueValidator

class Review(models.Model):
    user=models.ForeignKey(Customer,on_delete=models.CASCADE)
    food=models.ForeignKey(Food,null=True,on_delete=models.SET_NULL)
    rating=models.PositiveIntegerField(validators=[MinValueValidator(1),MaxValueValidator(5)])
    comment=models.CharField(max_length=300)
    
    
class RestaurantReview(models.Model):
    user=models.ForeignKey(Customer,on_delete=models.CASCADE,related_name="restaurant_review")
    vendor=models.ForeignKey(Vendor,null=True,on_delete=models.SET_NULL)
    rating=models.PositiveIntegerField(validators=[MinValueValidator(1),MaxValueValidator(5)])
    comment=models.CharField(max_length=300)
    
    
def create_cart(sender,created,instance,**kwargs):
    if created:
        Cart.objects.create(user=instance)



post_save.connect(create_cart,sender=Customer)



