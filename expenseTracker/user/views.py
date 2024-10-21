from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import *
from .serializers import *
from passlib.hash import pbkdf2_sha256
from django.contrib.auth import authenticate, login, logout
from rest_framework import status
from django.utils.decorators import decorator_from_middleware
import datetime
from utils.logger import *
from utils.extras import *
from utils.middleware import *
from django.middleware.csrf import get_token
from rest_framework import status

logger = setup_console_logger()

# Create your views here.
@api_view(['GET'])
@decorator_from_middleware(AuthenticationMiddleware)
def getUsers(request):
    logger.info("Received request to fetch all users.")
    user_id = request.COOKIES.get('user_id')
    email = request.COOKIES.get('email')
    
    if not user_id or not email:
        logger.warning("Authentication failed: Missing user_id or email in cookies.")
        response  = {
            'status': 'error',
            'message': "Authentication Failed",
            'status_code': status.HTTP_400_BAD_REQUEST ,
        }
        return Response(response)
    
    logger.info(f"Authenticated user with ID: {user_id}")
    data = User.objects.exclude(user_id=user_id).all()
    serializer = UserSerializer(data, many=True)
    user_count = len(data)
    
    logger.info(f"Fetched {user_count} users successfully.")
    
    return Response({
        'status': 'success',
        'message': "All Registered Data",
        'status_code': status.HTTP_200_OK,
        "available_user_count": user_count,
        "data": serializer.data,
    })


@api_view(['POST'])
def userRegister(request):
    logger.info("Received request for user registration.")
    serializer = UserSerializer(data=request.data)
    
    # Validate input fields
    if not request.data.get('email') or not request.data.get('password') or not request.data.get('mobile_no') or not request.data.get('name'):
        logger.warning("Registration failed: Missing required fields.")
        return Response({'status': 'error', 'message': 'All Fields are required'})

    if serializer.is_valid():
        logger.info(f"Validated registration data for email: {request.data.get('email')}")
        # Encrypt the password
        enc_password = pbkdf2_sha256.encrypt(serializer.validated_data['password'], rounds=12000, salt_size=32)
        user = serializer.save(password=enc_password)
        user_data = UserSerializer(user).data
        
        logger.info(f"User registered successfully: {user_data.get('email')}")
        
        return Response({ 
            'status': 'success',
            'message': 'User Registered successfully',
            'encrypted_password': enc_password,
            'user': user_data,  
        })
    
    logger.error(f"Registration failed: {serializer.errors}")
    return Response({
        'status': 'error',
        'message': serializer.errors
    })


@api_view(['POST'])
def userLogin(request):
    logger.info("Received login request.")
    
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        logger.warning("Login failed: Missing email or password.")
        response = {
            'status': 'error',
            'message': "All Fields Required",
            'status_code': status.HTTP_400_BAD_REQUEST,
        }
        return Response(response)

    try:
        user = User.objects.get(email=email)
        logger.info(f"Found user with email: {email}")
    except User.DoesNotExist:
        logger.warning(f"Login failed: User with email {email} does not exist.")
        return Response({
            'status': 'error',
            'message': 'User does not exist',
            'status_code': status.HTTP_204_NO_CONTENT
        })

    if is_valid_email(email) and user.verifyPassword(password):
        logger.info(f"Login successful for user {user.user_id}.")
        response = Response({
            'status': 'success',
            'message': 'Login successful',
            'user': {
                "user_id": user.user_id, 
                "name": user.name,
                "email": user.email,
            },
            "status": status.HTTP_200_OK
        }, status=status.HTTP_200_OK)

        expires_at = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        response.set_cookie('user_id', user.user_id, expires=expires_at, httponly=True, samesite='None')
        response.set_cookie('email', user.email, expires=expires_at, httponly=True, samesite='None')
        
        return response
    else:
        logger.warning(f"Login failed: Invalid password for user {email}.")
        response = {
            'status': 'error',
            'message': 'Invalid password or check email id',
            'status_code': status.HTTP_400_BAD_REQUEST
        }
        return Response(response)


@api_view(['POST'])
def userLogout(request):
    logger.info("Received logout request.")
    
    logout(request)
    logger.info("Logout successful.")
    
    return Response({
        'status': 'success',
        'message': 'Logout successful',
        'status_code': status.HTTP_200_OK,
    })
