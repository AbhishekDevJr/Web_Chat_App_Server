from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .serializers import CustomUserSerializer
from rest_framework.permissions import AllowAny

# Create your views here.

class UserLoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            if request.data.get('username') and request.data.get('password'):
                user = authenticate(username=request.data.get('username'), password=request.data['password'])
            
                if user:
                    token, created = Token.objects.get_or_create(user=user)
                    response = Response({'token' : token.key, 'createdAt' : created})
                    response.set_cookie(
                        key="auth_token",
                        value=token.key,
                        httponly=True,
                        secure=False,
                        samesite='Lax'
                    )
                    
                    return response
                else:
                    return Response({'error' : 'Invalid Credentials'}, status=400)
            else:
                return Response({'error' : 'Bad Request'}, status=400)
        except Exception as e:
            return Response({'error' : 'Unhandled Exception'}, status=500)
        

class UsersignupView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        try:
            serialized_data = CustomUserSerializer(data = request.data)
            
            if serialized_data.is_valid():
                serialized_data.save()
                return Response(serialized_data.data, status=201)
            return Response({'error' : 'Bad Request', 'message' : serialized_data.errors}, status=400)
        
        except Exception as e:
            return Response({'error' : 'Unhandled Exception'}, status=500)