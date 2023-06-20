from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
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
from django.contrib.auth import authenticate
from rest_framework import status
from django.middleware.csrf import get_token
# for just display 
from rest_framework.renderers import JSONRenderer

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

@api_view(['POST'])
def signup(request):
    if request.content_type != 'application/json':
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
        response = Response(
            {'error': 'Username and password are required', 'message': 'Please provide a valid username and password.'},
            status=status.HTTP_400_BAD_REQUEST
        )
        response.accepted_media_type = 'application/json'
        response.renderer_context = {}
        response.accepted_renderer = JSONRenderer()

        return response

    if len(username) < 3:
        print(55555555555555)
        response = Response(
            {'error': 'Invalid username', 'message': 'Username must be at least 3 characters long.'},
            status=status.HTTP_400_BAD_REQUEST
        )
        response.accepted_media_type = 'application/json'
        response.renderer_context = {}
        response.accepted_renderer = JSONRenderer()

        return response

    if not re.match(r'^\d{6}$', password):
        response = Response(
            {'error': 'Invalid password', 'message': 'Password must contain exactly 6 digits.'},
            status=status.HTTP_400_BAD_REQUEST
        )
        response.accepted_media_type = 'application/json'
        response.renderer_context = {}
        response.accepted_renderer = JSONRenderer()

        return response

    if not re.match(r'^\w+$', username):
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

        response = Response(response_data, status=status.HTTP_201_CREATED)
        response.accepted_media_type = 'application/json'
        response.renderer_context = {}
        response.accepted_renderer = JSONRenderer()

        return response

    except IntegrityError:
        response = Response(
            {'error': 'Username is already taken', 'message': 'The username you provided is already taken.'},
            status=status.HTTP_400_BAD_REQUEST
        )
        response.accepted_media_type = 'application/json'
        response.renderer_context = {}
        response.accepted_renderer = JSONRenderer()

        return response


@csrf_exempt
def login(request):
    if request.method == 'POST':
        try:
            data = JSONParser().parse(request)
        
            if len(data) != 2 or 'username' not in data or 'password' not in data:
                response = Response( {'error': 'Invalid request data','message':'please make sure of your keys and its value'},status=status.HTTP_400_BAD_REQUEST)
                response.accepted_media_type = 'application/json'
                response.renderer_context = {}
                # Set the accepted renderer to JSONRenderer
                response.accepted_renderer = JSONRenderer()
                return response
        except:
            response = Response( {'error': 'Invalid request data','message':'you have no keys in your request, or your key has no value'},status=status.HTTP_400_BAD_REQUEST)
            response.accepted_media_type = 'application/json'
            response.renderer_context = {}
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
            # Set the accepted renderer to JSONRenderer
            response.accepted_renderer = JSONRenderer()

            return response

        password_valid = user.check_password(password)

        if not password_valid:
            response = Response( {'error': 'Invalid password or password','message':'your password is incorrect'},
                status=status.HTTP_400_BAD_REQUEST)
            response.accepted_media_type = 'application/json'
            response.renderer_context = {}
            # Set the accepted renderer to JSONRenderer
            response.accepted_renderer = JSONRenderer()

            return response

        token, _ = Token.objects.get_or_create(user=user)

        response_data = {'token': str(token)}
        response_data['csrf_token'] = get_token(request)
        
        response = Response(response_data,status=status.HTTP_201_CREATED)
        response.accepted_media_type = 'application/json'
        response.renderer_context = {}
        # Set the accepted renderer to JSONRenderer
        response.accepted_renderer = JSONRenderer()

        return response
        # return Response(response_data, )
    response = Response( {'error': 'Invalid request method'},
                status=status.HTTP_405_METHOD_NOT_ALLOWED)
    response.accepted_media_type = 'application/json'
    response.renderer_context = {}
    # Set the accepted renderer to JSONRenderer
    response.accepted_renderer = JSONRenderer()

    return response

    