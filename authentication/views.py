from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.sessions.models import Session
from django.contrib.auth import authenticate
from .serializers import CustomUserSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .models import CustomUser
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login

# Create your views here.

class UserLoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            if request.data.get('username') and request.data.get('password'):
                friendlistres = []
                user = authenticate(username=request.data.get('username'), password=request.data['password'])
                
            
                if user:
                    friendlist = user.friends.all()
                
                    for friend in friendlist:
                        friendlistres.append(CustomUserSerializer(friend).data)
                    
                    token, created = Token.objects.get_or_create(user=user)
                    login(request, user)
                    response = Response({
                        'title' : 'Authentication Successful',
                        'msg' : 'User Successfully Authenticated',
                        'token' : token.key,
                        'createdAt' : created,
                        'currentUser' : CustomUserSerializer(user).data,
                        'friendList' : friendlistres,
                        'userinfo': CustomUserSerializer(user).data
                    })
                    
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
                'msg' : 'Unhandled Exception',
                'error': str(e)
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
            auth_token = request.headers.get('Authorization')
            
            if not auth_token or not auth_token.startswith('Token '):
                return Response({
                    'title': 'Auth Token Not Found.',
                    'msg': 'No Auth Token found for current User.'
                }, status=400)
                        
            token_key = auth_token.split(' ')[1]
            token_obj = Token.objects.get(key=token_key).delete()
            
            return Response({
            'title' : 'Logged Out',
            'msg' : 'Logged Out Successfully.'
        }, status = 200)
                
        
        except Token.DoesNotExist as e:
            return Response({
                'title': 'Auth Token does not Exists.',
                'mgs': str(e)
            }, status=400)
        
        except Token.MultipleObjectsReturned as e:
            return Response({
                'title': 'Multiple Token data found for current Token Key.',
                'msg': str(e)
            }, status=400)
        
        except Exception as e:
            return Response({
                'title' : 'Unhandled Exception',
                'msg' : 'Unhandled Exception'
            }, status=500)
        
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
                        'title' : 'User Found',
                        'msg' : 'Requested User Found.',
                        'user_data' : {
                        'username' : search_user.username,
                        'email' : search_user.email,
                        'firstname' : search_user.first_name if search_user.first_name else None,
                        'lastname' : search_user.last_name if search_user.last_name else None   
                        }
                    }, status=200)
                else:
                    return Response({'msg' : 'No user fount for the Specified Username.'}, status=200)
            else:
                return Response({'msg' : 'No Username found in the Request Payload.'}, status=400)
        
        except Exception as e:
            return Response({'msg' : 'Unhandled Exception'}, status=500)
        
class UserCheckAuthView(APIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        try:
            return Response({
                'title' : 'Auth Check',
                'msg' : 'User is Authenticated'
            },status=200)
        
        except Exception as e:
            return Response({
                'title' : 'Unhandled Server Error',
                'msg' : 'Unhandled Server Error'
            }, status=500)