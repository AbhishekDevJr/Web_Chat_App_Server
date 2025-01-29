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
    # authentication_classes = []
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
    # authentication_classes = []
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
                search_user = CustomUser.objects.filter(username = user_search_str).last()
                user_data = CustomUserSerializer(search_user).data
                
                if user_data:
                    return Response({
                        'message' : 'Requested user Found.',
                        'username' : user_data.username,
                        'firstname' : user_data.firstname,
                        'lastname' : user_data.lastname
                    }, status=200)
                else:
                    return Response({'message' : 'No user fount for the Specified Username.'}, status=200)
            else:
                return Response({'message' : 'No Username found in the Request Payload.'}, status=400)
        
        except Exception as e:
            return Response({'error' : 'Unhandled Exception'}, status=500)