from django.shortcuts import render
from rest_framework import mixins,generics
from vendor.serializers import VendorSerializer,CategorySerializer,FoodSerializer,OfferSerializer,ReviewSerializer,OrderSerializer,FoodViewSerializer,ProfileSerializer
from admin1.models import Vendor,Category,Food,Offer,Review,Order
from rest_framework.views import APIView,View
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet,ViewSet
from rest_framework.decorators import action
from rest_framework import authentication
from rest_framework import permissions
from rest_framework import serializers
from django.utils import timezone
from django.shortcuts import redirect
from django.urls import reverse
from django.http import JsonResponse
import requests
from datetime import datetime
from django.contrib.auth import logout
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView,status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token


from django.shortcuts import render
from rest_framework.response import Response


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        user_type = user.user_type
        
        return Response(data={'status':1,'data':{'token': token.key,'user_type': user_type,}})  



class VendorCreationView(APIView):
    def post(self,request,*args,**kwargs):
        serializer=VendorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user_type="vendor")
            return Response(data={'status':1,'data':serializer.data})
        else:
            error_messages = ' '.join([error for errors in serializer.errors.values() for error in errors])
            return Response(data={'status':0,'msg': error_messages}, status=status.HTTP_400_BAD_REQUEST)



class ProfileView(ViewSet):
    authentication_classes=[authentication.TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]
    
    def list(self, request, *args, **kwargs):
        user_id = request.user.id
        try:
            vendor = Vendor.objects.get(id=user_id)
            serializer = ProfileSerializer(vendor)
            return Response(data={'status':1,'data':serializer.data})
        except Vendor.DoesNotExist:
            return Response(data={'status':0,"msg": "Vendor does not exist"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, *args, **kwargs): 
        user_id = request.user.id
        try:
            vendor = Vendor.objects.get(id=user_id)
        except Vendor.DoesNotExist:
            return Response(data={'status':0,"msg": "Vendor does not exist"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProfileSerializer(instance=vendor, data=request.data)
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
    
    
    def create(self,request,*args,**kwargs):
        serializer=CategorySerializer(data=request.data)
        vendor_id=request.user.id
        print(vendor_id)
        vendor_object=Vendor.objects.get(id=vendor_id)
        if vendor_object:
            if serializer.is_valid():
                serializer.save(vendors=vendor_object)
                return Response(data={'status':1,'data':serializer.data})
            else:
                error_messages = ' '.join([error for errors in serializer.errors.values() for error in errors])
                return Response(data={'status':0,'msg': error_messages}, status=status.HTTP_400_BAD_REQUEST)        
        else:
            return Response(request,data={'status':0,'msg':"vendor not found"})
        
    def list(self,request,*args,**kwargs):
        vendor_id=request.user.id
        vendor_object=Vendor.objects.get(id=vendor_id)
        qs=Category.objects.filter(vendors=vendor_object)
        serializer=CategorySerializer(qs,many=True)
        return Response(data={'status':1,'data':serializer.data})
    
    
    def retrieve(self, request, *args, **kwargs):
        try:
            category=Category.objects.get(pk=kwargs.get("pk"))
        except category.DoesNotExist:
            return Response(data={'status':0,'msg': "category does not exist"},status=status.HTTP_404_NOT_FOUND)
        category_serializer = CategorySerializer(category)
        food_serializer = FoodSerializer(category.food_set.all(),many=True)
        response_data = category_serializer.data
        response_data['foods'] = food_serializer.data
        return Response(data={'status':1,'data': response_data})
    
    
    def destroy(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        instance=Category.objects.get(id=id)
        if instance.vendor==request.user.vendor:
            instance.delete()
            return Response(data={'status':1,"msg":"deleted"})
        else:
            return Response(data={'status':0,"msg":"permission denied"},status=status.HTTP_404_NOT_FOUND)
    
    
    @action(methods=["post"],detail=True)
    def add_food(self,request,*args,**kwargs):
        serializer=FoodSerializer(data=request.data)
        cat_id=kwargs.get("pk")
        category_obj=Category.objects.get(id=cat_id)
        vendor=request.user.id
        vendor_object=Vendor.objects.get(id=vendor) 
        if serializer.is_valid():
            serializer.save(category=category_obj,vendor=vendor_object,is_active=True)
            return Response(data={'status':1,'data':serializer.data})
        else:
            error_messages = ' '.join([error for errors in serializer.errors.values() for error in errors])
            return Response(data={'status':0,'msg': error_messages}, status=status.HTTP_400_BAD_REQUEST)        
   

class FoodView(ViewSet):
    authentication_classes=[authentication.TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]
    serializer_class = FoodSerializer


    def list(self,request,*args,**kwargs):
        vendor_id=request.user.id
        vendor_object=Vendor.objects.get(id=vendor_id)
        qs=Food.objects.filter(vendor=vendor_object)
        serializer=FoodViewSerializer(qs,many=True)
        return Response(data={'status':1,'data':serializer.data})
    
        
    def retrieve(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        qs=Food.objects.get(id=id)
        if qs.vendor==request.user.vendor:
            serializer=FoodViewSerializer(qs)
            return Response(data={'status':1,'data':serializer.data})
        else:
            return Response(data={'status':0,"msg":"permission denied"},status=status.HTTP_400_BAD_REQUEST)
    
    
    
    def update(self,request,*args,**kwargs): 
        id=kwargs.get("pk")
        obj=Food.objects.get(id=id)
        serializer=FoodSerializer(data=request.data,instance=obj)
        instance=Food.objects.get(id=id)
        if instance.vendor==request.user.vendor:
            if serializer.is_valid():
                serializer.save()
                return Response(data={'status':1,'data':serializer.data})
            else:
                error_messages = ' '.join([error for errors in serializer.errors.values() for error in errors])
                return Response(data={'status':0,'msg': error_messages}, status=status.HTTP_400_BAD_REQUEST)        
        else:
            return Response(data={'status':0,"msg":"permission denied"},status=status.HTTP_400_BAD_REQUEST)
        

    
    def destroy(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        instance=Food.objects.get(id=id)
        if instance.vendor==request.user.vendor:
            instance.delete()
            return Response(data={'status':1,"msg":"deleted"})
        else:
            return Response(data={'status':0,"msg":"permission denied"},status=status.HTTP_400_BAD_REQUEST)


    
    @action(methods=["post"],detail=True)
    def offer_add(self,request,*args,**kwargs):
        serializer=OfferSerializer(data=request.data)
        food_id=kwargs.get("pk")
        food_obj=Food.objects.get(id=food_id)
        vendor=request.user.id
        vendor_object=Vendor.objects.get(id=vendor) 
        if serializer.is_valid():
            serializer.save(food=food_obj,vendors=vendor_object)
            return Response(data={'status':1,'data':serializer.data})
        else:
            error_messages = ' '.join([error for errors in serializer.errors.values() for error in errors])
            return Response(data={'status':0,'msg': error_messages}, status=status.HTTP_400_BAD_REQUEST)        
    
    @action(methods=["get"],detail=True)  
    def review_list(self,request,*args,**kwargs):
        food_id=kwargs.get("pk")
        food_obj=Food.objects.get(id=food_id)
        qs=Review.objects.filter(food=food_obj)
        serializer=ReviewSerializer(qs,many=True)
        return Response(data={'status':1,'data':serializer.data})
    
        

class OfferView(ViewSet):
    authentication_classes=[authentication.TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]
    serializer_class=OfferSerializer


    def list(self,request,*args,**kwargs):
        qs=Offer.objects.filter(vendors=request.user.vendor,due_date__gte=timezone.now())
        serializer=OfferSerializer(qs,many=True)
        return Response(data={'status':1,'data':serializer.data})
    
    def destroy(self, request, *args, **kwargs):
        offer_id = kwargs.get("pk")
        try:
            offer = Offer.objects.get(id=offer_id)
        except Offer.DoesNotExist:
            return Response(data={'status':0,"msg": "Offer does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
        if offer.vendors == request.user.vendor:
            offer.delete()
            return Response(data={'status':1,"msg": "Offer deleted"})
        else:
            return Response(data={'status':0,"msg":"Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        

class OrderView(ViewSet):
    authentication_classes=[authentication.TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]


    def list(self,request,*args,**kwargs):
        vendor_id=request.user.id
        qs=Order.objects.filter(cart__cartitem__food__vendor=vendor_id)
        serializer=OrderSerializer(qs,many=True)
        return Response(data={'status':1,'data':serializer.data})
           

   