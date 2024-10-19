# myapp/middleware.py
from django.shortcuts import redirect
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from user.models import User
from django.contrib.auth.middleware import get_user
from django.urls import reverse
from rest_framework.response import Response
from .logger import setup_console_logger
from rest_framework import status

logger = setup_console_logger()

class AuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.path.startswith('/login/') or request.path.startswith('/static/'):
            return None
        email_id = request.COOKIES.get('email')
        user_id = request.COOKIES.get('user_id')
        if not user_id or not email_id:
            login_url = reverse('user-login')  # This will generate '/auth/login/' assuming 'login' is the URL name
            response  = {
                'status': 'error',
                'message': "Authentication Failed",
                'status_code': status.HTTP_400_BAD_REQUEST ,
            }
            return Response(response)

        try:
            user = User.objects.get(pk=user_id)
            request.user = user
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)})