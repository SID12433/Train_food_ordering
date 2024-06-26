from django.shortcuts import render
from admin1.models import Customer,Food,Review,Order,Cart,CartItem,Category,Vendor
from userapi.serializers import CustomerSerializer,CategorySerializer,VendorSerializer,FoodSerializer,CartSerializer,CartItemsSerializer,ReviewSerializer,OrderSerializer,RestaurantReviewSerializer,ProfileSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet,ViewSet
from rest_framework.decorators import action
from rest_framework import authentication
from rest_framework import permissions
from rest_framework import serializers
from django.utils import timezone
import razorpay
from rest_framework import status
from django.contrib.auth import logout

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token



# Create your views here.

class CustomerCreationView(APIView):
    def post(self,request,*args,**kwargs):
        serializer=CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user_type="customer")
            return Response(data={'status':1,'data':serializer.data})
        else:
            error_messages = ' '.join([error for errors in serializer.errors.values() for error in errors])
            return Response(data={'status':0,'msg': error_messages}, status=status.HTTP_400_BAD_REQUEST)        


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        user_type = user.user_type
        
        return Response(data={'status':1,'data':{'token': token.key,'user_type': user_type,}})        
        
        
class ProfileView(ViewSet):
    authentication_classes=[authentication.TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]
    
    def list(self, request, *args, **kwargs):
        user_id = request.user.id
        try:
            customer = Customer.objects.get(id=user_id)
            serializer = ProfileSerializer(customer)
            return Response(data={'status':1,'data':serializer.data})
        except customer.DoesNotExist:
            return Response(data={'status':0,"msg": "Customer does not exist"}, status=status.HTTP_404_NOT_FOUND)



    def put(self, request, *args, **kwargs): 
        user_id = request.user.id
        try:
            customer = Customer.objects.get(id=user_id)
        except customer.DoesNotExist:
            return Response(data={'status':0,"msg": "Customer does not exist"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProfileSerializer(instance=customer, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data={'status':1,'data':serializer.data})
        else:
            error_messages = ' '.join([error for errors in serializer.errors.values() for error in errors])
            return Response(data={'status':0,'msg': error_messages}, status=status.HTTP_400_BAD_REQUEST)        
        
        
        
class CategoryView(ViewSet):
    authentication_classes=[authentication.TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]
    serializer_class = CategorySerializer
        
    def list(self,request,*args,**kwargs):
        qs=Category.objects.filter(is_active=True)
        serializer=CategorySerializer(qs,many=True)
        return Response(data={'status':1,'data':serializer.data})


    def retrieve(self, request, *args, **kwargs):
        try:
            category = Category.objects.get(pk=kwargs.get("pk"))
        except category.DoesNotExist:
            return Response(data={'status':0,"msg": "category does not exist"},status=status.HTTP_404_NOT_FOUND)
        category_serializer = CategorySerializer(category)
        food_serializer = FoodSerializer(category.food_set.all(), many=True)
        response_data = category_serializer.data
        response_data['foods'] = food_serializer.data
        return Response(data={'status':1,'data':response_data})



    
class VendorView(ViewSet):
    authentication_classes=[authentication.TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]
    serializer_class = VendorSerializer
        
        
    def list(self,request,*args,**kwargs):
        qs=Vendor.objects.all()
        serializer=VendorSerializer(qs,many=True)
        return Response(data={'status':1,'data':serializer.data})
    

    
    def retrieve(self, request, *args, **kwargs):
        try:
            vendor = Vendor.objects.get(pk=kwargs.get("pk"))
        except vendor.DoesNotExist:
            return Response(data={'status':0,"msg": "vendor does not exist"},status=status.HTTP_404_NOT_FOUND)
        vendor_serializer=VendorSerializer(vendor)
        category_serializer=CategorySerializer(vendor.category_set.all(), many=True)
        review_serializer=RestaurantReviewSerializer(vendor.restaurantreview_set.all(), many=True)
        response_data=vendor_serializer.data
        response_data['categories'] = category_serializer.data
        response_data['reviews'] = review_serializer.data
        return Response(data={'status':1,'data':response_data})
    
    
    @action(methods=["post"],detail=True)
    def add_restaurantreview(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        vendor_object=Vendor.objects.get(id=id) 
        user=request.user.customer
        serializer=RestaurantReviewSerializer(data=request.data)
        

        if serializer.is_valid():
            serializer.save(user=user,vendor=vendor_object)
            return Response(data={'status':1,'data':serializer.data})
        error_messages = ' '.join([error for errors in serializer.errors.values() for error in errors])
        return Response(data={'status':0,'msg': error_messages}, status=status.HTTP_400_BAD_REQUEST)    
        
    
class FoodView(ViewSet):
    authentication_classes=[authentication.TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]
    serializer_class = FoodSerializer
        
    def list(self,request,*args,**kwargs):  
        qs=Food.objects.filter(is_active=True)
        serializer=FoodSerializer(qs,many=True)
        return Response(data={'status':1,'data':serializer.data})
    
    
    @action(methods=["post"],detail=True)
    def add_to_cart(self, request, *args, **kwargs):
        food_id = kwargs.get("pk")
        food_object = Food.objects.get(id=food_id)
        cart_object = request.user.customer.cart

        existing_cart_item=cart_object.cartitem.filter(food=food_object).first()
        
        if existing_cart_item:
            new_quantity=int(request.data.get('quantity',1))
            existing_cart_item.quantity+=new_quantity
            existing_cart_item.save()
            serializer=CartItemsSerializer(existing_cart_item)
            return Response(data={'status':1,'data':serializer.data})
        else:
            serializer=CartItemsSerializer(data=request.data)
            
            if serializer.is_valid():
                serializer.save(cart=cart_object,food=food_object,is_active=True)
                return Response(data={'status':1,'data':serializer.data})
            
            error_messages = ' '.join([error for errors in serializer.errors.values() for error in errors])
            return Response(data={'status':0,'msg': error_messages}, status=status.HTTP_400_BAD_REQUEST)    
        

    
    @action(methods=["post"],detail=True)
    def add_review(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        food_object=Food.objects.get(id=id) 
        user=request.user.customer
        serializer=ReviewSerializer(data=request.data)
        

        if serializer.is_valid():
            serializer.save(user=user,food=food_object)
            return Response(data={'status':1,'data':serializer.data})
        error_messages = ' '.join([error for errors in serializer.errors.values() for error in errors])
        return Response(data={'status':0,'msg': error_messages}, status=status.HTTP_400_BAD_REQUEST)    
    
     
razorpay_client = razorpay.Client(auth=("rzp_test_dGbzyUivWJNxDV", "4iYJQWiT6WT7xYcl1JdHSD3a"))


class CartView(ViewSet):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CartSerializer

    def list(self, request, *args, **kwargs):
        user = request.user.customer
        qs = Cart.objects.filter(user=user)
        serializer = CartSerializer(qs, many=True)
        return Response(data={'status':1,'data':serializer.data})
    

    @action(methods=["post"], detail=True)
    def place_order(self, request, *args, **kwargs):
        cart_object = request.user.customer.cart
        user = request.user.customer
        amount = cart_object.calculate_total_amount
        serializer = OrderSerializer(data=request.data)

        if serializer.is_valid():
            order = serializer.save(user=user, cart=cart_object, order_amount=amount)

            try:
                order_amount = int(order.order_amount)
                order_data = {
                    'amount': order_amount,
                    'currency': 'INR',
                    'receipt': f'order_receipt_{order.id}',
                    'payment_capture': 1
                }

                order_response = razorpay_client.order.create(order_data)
                razorpay_order_id = order_response['id']

                order.razorpay_order_id = razorpay_order_id
                order.save()

                user_info={'name':user.name,'phone':user.phone}

                return Response({
                    'razorpay_order_id': razorpay_order_id,
                    'order_id': order.id,
                    'amount': order_amount,
                    'user': user_info,
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                print(e)
                return Response(data={'status':0,'msg':'Error processing payment'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        error_messages = ' '.join([error for errors in serializer.errors.values() for error in errors])
        return Response(data={'status':0,'msg': error_messages}, status=status.HTTP_400_BAD_REQUEST)    


class OrderView(ViewSet):
    authentication_classes=[authentication.TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]


    def list(self,request,*args,**kwargs):
        user_id=request.user.id
        qs=Order.objects.filter(user=user_id)
        serializer=OrderSerializer(qs,many=True)
        return Response(data={'status':1,'data':serializer.data})
    
    def retrieve(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        qs=Order.objects.get(id=id)
        serializer=OrderSerializer(qs)
        return Response(data={'status':1,'data':serializer.data})

    

class VendorSearchView(APIView):
    def post(self, request, format=None):
        address = request.data.get('location')
        if not address:
            return Response({'status':0,"msg": "Address parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
        vendors = Vendor.objects.filter(address__icontains=address)
        serializer = VendorSerializer(vendors, many=True)
        return Response(data={'status':1,'data':serializer.data})
    
    
class FoodSearchView(APIView):
    def post(self, request, format=None):
        food = request.data.get('food')
        type = request.data.get('type')

        if not food and not type:
            return Response(data={'status':0,"msg": "At least one of 'food' or 'type' parameters is required."}, status=status.HTTP_400_BAD_REQUEST)
        filter_conditions = {}
        if food:
            filter_conditions['name__icontains'] = food
        if type:
            filter_conditions['type__icontains'] = type
        foods = Food.objects.filter(**filter_conditions)
        if foods.exists():
            serializer = FoodSerializer(foods, many=True)
            return Response(data={'status':1,'data':serializer.data})
        else:
            return Response(data={"status":0,"msg": "No food items found matching the search criteria."}, status=status.HTTP_404_NOT_FOUND)





