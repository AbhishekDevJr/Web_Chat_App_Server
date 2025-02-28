from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .serializers import CustomUserSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .models import CustomUser

# Create your views here.

class UserLoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            if request.data.get('username') and request.data.get('password'):
                user = authenticate(username=request.data.get('username'), password=request.data['password'])
            
                if user:
                    token, created = Token.objects.get_or_create(user=user)
                    response = Response({
                        'title' : 'Authentication Successful',
                        'msg' : 'User Successfully Authenticated',
                        'token' : token.key, 
                        'createdAt' : created,
                        'friendList' : CustomUserSerializer(user).data
                    })
                    response.set_cookie(
                        key="auth_token",
                        value=token.key,
                        httponly=True,
                        secure=False,
                        samesite='Lax'
                    )
                    
                    return response
                else:
                    return Response({
                        'msg' : 'Invalid Credentials'
                    }, status=400)
            else:
                return Response({
                    'msg' : 'Bad Request'
                }, status=400)
        except Exception as e:
            return Response({
                'msg' : 'Unhandled Exception'
            }, status=500)
        
class UsersignupView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        try:
            serialized_data = CustomUserSerializer(data = request.data)
            
            if serialized_data.is_valid():
                serialized_data.save()
                return Response({
                    "title" : "User Registered",
                    "msg" : "User Registered Successfully.",
                    "data" :serialized_data.data,
                    }, status=201)
            return Response({
                'title' : 'Bad Request', 
                'msg' : serialized_data.errors
                }, status=400)
        
        except Exception as e:
            return Response({
                'title' : 'Unhandled Server Error',
                'msg' : 'Unhandled Server Error'
                }, status=500)
        
class UserLogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        try:
            request.user.auth_token.delete()
            
            response = Response({'message' : 'Successfully Logged Out.'}, status = 200)
            response.delete_cookie('auth_token')
            
            return response
        
        except Exception as e:
            return Response({'error' : 'Unhandled Exception'}, status=500)
        
class UserSearchView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        try:
            user_search_str = request.data['username']
            
            if user_search_str:
                search_user = CustomUser.objects.filter(email__icontains = user_search_str).last()
                
                if search_user:
                    return Response({
                        'message' : 'Requested User Found.',
                        'user_data' : {
                        'username' : search_user.username,
                        'email' : search_user.email,
                        'firstname' : search_user.first_name if search_user.first_name else None,
                        'lastname' : search_user.last_name if search_user.last_name else None   
                        }
                    }, status=200)
                else:
                    return Response({'message' : 'No user fount for the Specified Username.'}, status=200)
            else:
                return Response({'message' : 'No Username found in the Request Payload.'}, status=400)
        
        except Exception as e:
            return Response({'error' : 'Unhandled Exception'}, status=500)