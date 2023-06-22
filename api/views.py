from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions

from .serializers import TodoSerializer, TodoToggleCompleteSerializer
from todo.models import Todo
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from django.db import IntegrityError
from rest_framework.authtoken.models import Token
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from django.middleware.csrf import get_token
# for just display 
from rest_framework.renderers import JSONRenderer
from .models import CustomUser
from .serializers import CustomUserSerializer
from rest_framework.views import APIView
from rest_framework import permissions


User = get_user_model()

class CustomUserAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return get_object_or_404(CustomUser, user=self.request.user)

    def put(self, request, *args, **kwargs):
        custom_user = self.get_object()
        serializer = self.serializer_class(custom_user, data=request.data, partial=True)
        if serializer.is_valid():
            custom_user.save_profile_pic(request)
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class TodoList(generics.ListAPIView):
    # ListAPIView requires two mandatory attributes, serializer_class and
    # queryset.
    # We specify TodoSerializer which we have earlier implemented
    serializer_class = TodoSerializer
    def get_queryset(self):
        user = self.request.user
        return Todo.objects.filter(user=user).order_by('-created')

class TodoListCreate(generics.ListCreateAPIView):
    # ListAPIView requires two mandatory attributes, serializer_class and
    # queryset.
    # We specify TodoSerializer which we have earlier implemented
    serializer_class = TodoSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        user = self.request.user
        return Todo.objects.filter(user=user).order_by('-created')
    def perform_create(self, serializer):
        #serializer holds a django model
        serializer.save(user=self.request.user)

class TodoRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TodoSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        user = self.request.user
         # user can only update, delete own posts
        return Todo.objects.filter(user=user)


class TodoToggleComplete(generics.UpdateAPIView):
    serializer_class = TodoToggleCompleteSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        user = self.request.user
        return Todo.objects.filter(user=user)
    def perform_update(self,serializer):
        serializer.instance.completed=not(serializer.instance.completed)
        serializer.save()

User = get_user_model()
import re

# عملية التسجيل
# Signup process
@api_view(['POST'])
def signup(request):
    if request.content_type != 'application/json':
        # رسالة خطأ عندما يكون نوع الطلب غير JSON
        # Error message when the request type is not JSON
        response = Response(
            {'error': 'Request data is not in JSON format', 'message': 'Please send a valid JSON payload.'},
            status=status.HTTP_400_BAD_REQUEST
        )
        response.accepted_media_type = 'application/json'
        response.renderer_context = {}
        response.accepted_renderer = JSONRenderer()

        return response

    data = JSONParser().parse(request)
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        # رسالة خطأ عندما يكون اسم المستخدم أو كلمة المرور غير موجودة
        # Error message when either username or password is missing
        response = Response(
            {'error': 'Username and password are required', 'message': 'Please provide a valid username and password.'},
            status=status.HTTP_400_BAD_REQUEST
        )
        response.accepted_media_type = 'application/json'
        response.renderer_context = {}
        response.accepted_renderer = JSONRenderer()

        return response

    if len(username) < 3:
        # رسالة خطأ عندما يكون اسم المستخدم أقل من 3 أحرف
        # Error message when the username is less than 3 characters
        response = Response(
            {'error': 'Invalid username', 'message': 'Username must be at least 3 characters long.'},
            status=status.HTTP_400_BAD_REQUEST
        )
        response.accepted_media_type = 'application/json'
        response.renderer_context = {}
        response.accepted_renderer = JSONRenderer()

        return response

    if not re.match(r'^\d{6}$', password):
        # رسالة خطأ عندما تحتوي كلمة المرور على أكثر أو أقل من 6 أرقام
        # Error message when the password does not contain exactly 6 digits
        response = Response(
            {'error': 'Invalid password', 'message': 'Password must contain exactly 6 digits.'},
            status=status.HTTP_400_BAD_REQUEST
        )
        response.accepted_media_type = 'application/json'
        response.renderer_context = {}
        response.accepted_renderer = JSONRenderer()

        return response

    if not re.match(r'^\w+$', username):
        # رسالة خطأ عندما يحتوي اسم المستخدم على حروف وأرقام وشرطات سفلية فقط
        # Error message when the username contains characters other than alphanumeric and underscores
        response = Response(
            {'error': 'Invalid username', 'message': 'Username can only contain alphanumeric characters and underscores.'},
            status=status.HTTP_400_BAD_REQUEST
        )
        response.accepted_media_type = 'application/json'
        response.renderer_context = {}
        response.accepted_renderer = JSONRenderer()

        return response

    UserModel = get_user_model()

    try:
        user = UserModel.objects.create_user(username=username, password=password)
        token, _ = Token.objects.get_or_create(user=user)

        response_data = {'token': str(token)}
        response_data['csrf_token'] = get_token(request)

        # رسالة نجاح عند إنشاء حساب جديد
        # Success message when a new account is created
        response = Response(response_data, status=status.HTTP_201_CREATED)
        response.accepted_media_type = 'application/json'
        response.renderer_context = {}
        response.accepted_renderer = JSONRenderer()

        return response

    except IntegrityError:
        # رسالة خطأ عندما يتم استخدام اسم مستخدم موجود بالفعل
        # Error message when the username is already taken
        response = Response(
            {'error': 'Username is already taken', 'message': 'The username you provided is already taken.'},
            status=status.HTTP_400_BAD_REQUEST
        )
        response.accepted_media_type = 'application/json'
        response.renderer_context = {}
        response.accepted_renderer = JSONRenderer()

        return response

# في هذا العرض، نقوم بتسجيل الدخول باستخدام اسم المستخدم وكلمة المرور وإرجاع رمز مميز.
# In this view, we log in using the username and password and return an access token.

# يتم تحويل هذا العرض إلى CSRF
# This view is CSRF exempted
@csrf_exempt
def login(request):
    if request.method == 'POST':
        try:
            data = JSONParser().parse(request)
        
            # التحقق من أن بيانات الطلب صالحة (تحتوي على اسم المستخدم وكلمة المرور)
            # Check if the request data is valid (contains the username and password)
            if len(data) != 2 or 'username' not in data or 'password' not in data:
                response = Response( {'error': 'Invalid request data','message':'please make sure of your keys and its value'},status=status.HTTP_400_BAD_REQUEST)
                response.accepted_media_type = 'application/json'
                response.renderer_context = {}
                # تعيين البرنامج العارض المقبول على JSONRenderer
                # Set the accepted renderer to JSONRenderer
                response.accepted_renderer = JSONRenderer()
                return response
        except:
            response = Response( {'error': 'Invalid request data','message':'you have no keys in your request, or your key has no value'},status=status.HTTP_400_BAD_REQUEST)
            response.accepted_media_type = 'application/json'
            response.renderer_context = {}
            # تعيين البرنامج العارض المقبول على JSONRenderer
            # Set the accepted renderer to JSONRenderer
            response.accepted_renderer = JSONRenderer()
            return response

        username = data.get('username')
        password = data.get('password')
        
        UserModel = get_user_model()

        try:
            user = UserModel.objects.get(username=username)
        except UserModel.DoesNotExist:
            response = Response( {'error': 'Invalid username ','message':'your username is incorrect'},
                status=status.HTTP_400_BAD_REQUEST)
            response.accepted_media_type = 'application/json'
            response.renderer_context = {}
            # تعيين البرنامج العارض المقبول على JSONRenderer
            # Set the accepted renderer to JSONRenderer
            response.accepted_renderer = JSONRenderer()

            return response

        password_valid = user.check_password(password)

        if not password_valid:
            response = Response( {'error': 'Invalid password or password','message':'your password is incorrect'},
                status=status.HTTP_400_BAD_REQUEST)
            response.accepted_media_type = 'application/json'
            response.renderer_context = {}
            # تعيين البرنامج العارض المقبول على JSONRenderer
            # Set the accepted renderer to JSONRenderer
            response.accepted_renderer = JSONRenderer()

            return response

        token, _ = Token.objects.get_or_create(user=user)

        response_data = {'token': str(token)}
        response_data['csrf_token'] = get_token(request)
        
        response = Response(response_data,status=status.HTTP_201_CREATED)
        response.accepted_media_type = 'application/json'
        response.renderer_context = {}
        # تعيين البرنامج العارض المقبول على JSONRenderer
        # Set the accepted renderer to JSONRenderer
        response.accepted_renderer = JSONRenderer()

        return response
        # return Response(response_data, )
    response = Response( {'error': 'Invalid request method'},
                status=status.HTTP_405_METHOD_NOT_ALLOWED)
    response.accepted_media_type = 'application/json'
    response.renderer_context = {}
    # تعيين البرنامج العارض المقبول على JSONRenderer
    # Set the accepted renderer to JSONRenderer
    response.accepted_renderer = JSONRenderer()

    return 
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.utils.encoding import force_bytes, force_text

from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

# class ResetPasswordView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request, *args, **kwargs):
#         email = request.data.get('email')
#         username = request.data.get('username')

#         if not email:
#             return Response({'error': 'Please provide your email address'}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             user = User.objects.get(username=username)
#         except User.DoesNotExist:
#             return Response({'error': 'User with this email address does not exist'}, status=status.HTTP_404_NOT_FOUND)

#         uid = urlsafe_base64_encode(force_bytes(user.pk))
#         token = default_token_generator.make_token(user)

#         reset_url = reverse('reset-password-confirm', kwargs={'uidb64': uid, 'token': token})
#         reset_url = request.build_absolute_uri(reset_url)

#         send_mail(
#             'Reset your password',
#             f'Please click on this link to reset your password: {reset_url}',
#             'urfitness96@gmail.com',
#             [email],
#             fail_silently=False,
#         )

#         return Response({'success': f'Password reset link has been sent to {email}'}, status=status.HTTP_200_OK)
    

    
# class ResetPasswordConfirmView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request, uidb64, token, *args, **kwargs):
#         try:
#             uid = force_text(urlsafe_base64_decode(uidb64))
#             user = User.objects.get(pk=uid)
#         except (TypeError, ValueError, OverflowError, User.DoesNotExist):
#             user = None

#         if user is not None and default_token_generator.check_token(user, token):
#             new_password = request.data.get('new_password')
#             confirm_password = request.data.get('confirm_password')

#             if new_password != confirm_password:
#                 return Response({'error': 'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)

#             if len(new_password) < 8:
#                 return Response({'error': 'Password must be at least 8 characters long'}, status=status.HTTP_400_BAD_REQUEST)

#             user.set_password(new_password)
#             user.save()

#             return Response({'success': 'Password has been reset'}, status=status.HTTP_200_OK)

#         return Response({'error': 'Invalid reset link'}, status=status.HTTP_400_BAD_REQUEST)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView


class ChangePasswordView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')

        # Verify that the old password is correct
        if not user.check_password(old_password):
            return Response({'error': 'Old password is incorrect','message': 'Old password is incorrect try again.'}, status=status.HTTP_400_BAD_REQUEST)
        if not re.match(r'^\d{6}$', new_password):
            # رسالة خطأ عندما تحتوي كلمة المرور على أكثر أو أقل من 6 أرقام
            # Error message when the password does not contain exactly 6 digits
            response = Response(
                {'error': 'Invalid password', 'message': 'Password must contain exactly 6 digits.'},
                status=status.HTTP_400_BAD_REQUEST
            )
            response.accepted_media_type = 'application/json'
            response.renderer_context = {}
            response.accepted_renderer = JSONRenderer()

            return response
        # Verify that the new password and confirm password match
        if new_password != confirm_password:
            return Response({'error': 'Passwords do not match','message': 'Your passwords  is not match try again.'}, status=status.HTTP_400_BAD_REQUEST)

        # Verify that the new password is not the same as the old password
        if new_password == old_password:
            return Response({'error': 'New password must be different from old password','message': 'Old password is same as the new one try change it.'}, status=status.HTTP_400_BAD_REQUEST)

        # Set the new password and save the user
        user.set_password(new_password)
        user.save()

        # Invalidate existing tokens for the user
        Token.objects.filter(user=user).delete()

        return Response({'success': 'Password has been changed','message': 'Congratulations.'}, status=status.HTTP_200_OK)
