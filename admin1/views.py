from django.shortcuts import render
from admin1.models import Customer,Food,Review,Order,Cart,CartItem,Category,Vendor
from userapi.serializers import CustomerSerializer,CategorySerializer,VendorSerializer,FoodSerializer,CartSerializer,CartItemsSerializer,ReviewSerializer,OrderSerializer,RestaurantReviewSerializer
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


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        user_type = user.user_type
        
        return Response(data={'status':1,'data':{'token': token.key,'user_type': user_type,}})  


class VendorView(ViewSet):
    authentication_classes=[authentication.TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]


    def list(self,request,*args,**kwargs):
        qs=Vendor.objects.all()
        serializer=VendorSerializer(qs,many=True)
        return Response(data={'status':1,'data':serializer.data})
    
        
    def retrieve(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        qs=Vendor.objects.get(id=id)
        serializer=VendorSerializer(qs)
        return Response(data={'status':1,'data':serializer.data})

        

class CustomerView(ViewSet):
    authentication_classes=[authentication.TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]


    def list(self,request,*args,**kwargs):
        qs=Customer.objects.all()
        serializer=CustomerSerializer(qs,many=True)
        return Response(data={'status':1,'data':serializer.data})
    
        
    def retrieve(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        qs=Customer.objects.get(id=id)
        serializer=CustomerSerializer(qs)
        return Response(data={'status':1,'data':serializer.data})
    
    
class OrdersView(ViewSet):
    authentication_classes=[authentication.TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]


    def list(self,request,*args,**kwargs):
        qs=Order.objects.all()
        serializer=OrderSerializer(qs,many=True)
        return Response(data={'status':1,'data':serializer.data})
    
        
    def retrieve(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        qs=Order.objects.get(id=id)
        serializer=OrderSerializer(qs)
        return Response(data={'status':1,'data':serializer.data})
