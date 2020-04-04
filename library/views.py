#import restframework modles
from rest_framework.pagination import  PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.generics import ListAPIView
from rest_framework.permissions import (
    BasePermission,
    IsAuthenticated,
    SAFE_METHODS
)

from rest_framework_jwt.settings import api_settings
jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
from rest_framework_simplejwt.tokens import RefreshToken

# import django exception modules and datetime
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import Q
from datetime import datetime


#import model classes
from django.contrib.auth import authenticate
from django.contrib.auth.models import Group
from library.models import User, RequestBook, TimePeriod, Book
from django.contrib.auth.models import Permission

# import serializers class
from library.serializers import (
    PermissionSerializer,
    UserSerializer,
    BookSerializer,
    RequestBookSerializer
)


class Login(APIView):
    """ 
    login api for all user types admin, staff and user
    """
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        username = request.data.get("username")
        password = request.data.get("password")
        if username is None or password is None:
            return Response({'status': 'failed','error': 'Please provide username and password'},
                            status=HTTP_400_BAD_REQUEST)
        user = authenticate(username=username, password=password)
        if not user:
            return Response({'status': 'failed','error': 'Invalid Credentials'},
                            status=HTTP_404_NOT_FOUND)
        elif user.groups.filter(name='user').exists():
            try:
                set_time = TimePeriod.objects.last()
                if not set_time.start_time <= datetime.now().time() < set_time.end_time:
                    return Response({'status': 'failed', 'error': 'Not valid time to request user'}) 
            except ObjectDoesNotExist:
                return Response({'status': 'failed', 'error': 'Please Set time period'})

        serializer = UserSerializer(user)
        refresh = RefreshToken.for_user(user)

        return Response({
            'token': str(refresh.access_token), 
            'refresh': str(refresh),
            'data': serializer.data}, status=HTTP_200_OK)


class UserPermission(BasePermission):
    """
        create user by admin and checking permission 
    """
    def has_permission(self, request, view):
        group =request.user.groups.values_list('name', flat=True)[0]
        return group == 'admin'


class RegistrationView(APIView):
    """ 
    create all user types using this api like admin, staff and user
    """

    permission_classes = (IsAuthenticated, UserPermission,)

    def get(self, request, pk, format=None):
        try:
            user = User.objects.get(pk=pk)
            serializer = UserSerializer(user)
            return Response({'status': 'success', 'data': serializer.data})
        except ObjectDoesNotExist:
            return Response({'status': 'failed','error': 'Object does not exist'},
                            status=HTTP_400_BAD_REQUEST)
    
    def post(self, request, format=None):
        with transaction.atomic():
            user_data = request.data
            if User.objects.filter(username=user_data.get('username')).exists():
                return Response({'status': 'failed', 'error': 'username already exists'})
            else:
                user_obj = User.objects.create_user(
                    username = user_data.get('username'),
                    first_name = user_data.get('first_name'),
                    last_name = user_data.get('last_name'),
                    email = user_data.get('email'),
                    password=user_data.get('password'),
                    phone_no=user_data.get('phone_no')
                )
                group_name = user_data.get('group')
                if group_name:
                    grp, created = Group.objects.get_or_create(
                        name=group_name)
                    user_obj.groups.add(grp)
                return Response({'status': 'success', 'msg': 'User Created Successfully'})


    def put(self, request, pk, format=None):
        user_obj = User.objects.get(pk=pk)
        data = request.data
        try:
            user_obj.first_name = data.get('first_name', user_obj.first_name)
            user_obj.last_name = data.get('last_name', user_obj.last_name)
            user_obj.email = data.get('email', user_obj.email)
            user_obj.email = data.get('phone_no', user_obj.phone_no)
            return Response({'status': 'success'})
        except ObjectDoesNotExist:
            return Response({'status': 'failed','error': 'Object does not exist'},
                            status=HTTP_400_BAD_REQUEST)


class BookPermission(BasePermission):
    def has_permission(self, request, view):
        group = request.user.groups.values_list('name', flat=True)[0]
        valid_staff = request.user.has_perm('library.staff_add_book')
        valid_user = request.user.has_perm('library.user_read_book')
        if group == 'staff' and request.method == 'POST':
            return valid_staff
        elif group == 'user' and request.method == 'GET':
            return valid_user
        else:
            return group == 'admin'


class BookCreate(generics.CreateAPIView):
    """ 
    To crate book, both admin and staff 
    can add book with permission 
    """
    permission_classes = (IsAuthenticated, BookPermission)
    serializer_class = BookSerializer


class PagesPagination(PageNumberPagination):
    """ 
    To set default book list pagination size
    """
    page_size = 10

class BookListView(generics.ListAPIView):
    """ 
    To get 10 books at a time and we can paginate over it
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = BookSerializer
    pagination_class = PagesPagination
    
    def get_queryset(self):
        return Book.objects.all()


class BookDetails(generics.RetrieveUpdateDestroyAPIView):
    """ 
    Get, update and delete book using this api
    """
    serializer_class = BookSerializer
    permission_classes = (IsAuthenticated, BookPermission)

    def get_queryset(self):
        return Book.objects.filter(id=self.kwargs['pk'])


class RequestCreate(APIView):
    """ 
    Create actual user for the app
    """
    permission_classes = (IsAuthenticated,)
    
    def post(self, request, format=None):
        with transaction.atomic():
            data = request.data
            book = Book.objects.get(id=data.get('book_id'))
            if book.available_copies <= 0:
                return Response({'status': 'error', 'error': 'This book is not available'})
            else:
                req_obj = RequestBook.objects.create(
                    customer_id = data.get('customer_id'),
                    book_id = data.get('book_id'),
                    issue_date = data.get('issue_date'),
                    return_date = data.get('return_date'),
                    status=data.get('status')
                )
                book.available_copies = book.available_copies - 1
                book.save()      
            return Response({'status': 'success', 'msg': 'successfully requested'})


class GrantPermission(APIView):
    """
    Add permission for staff to grant add new books into the system
    """
    permission_classes = (IsAuthenticated,)
    
    def post(self, request, format=None):
        with transaction.atomic():
            data = request.data
            permission = Permission.objects.get(id=data.get('permission_id'))
            user = User.objects.get(id=data.get('user_id')) 
            group_name = data.get('group')
            if group_name == 'user':
                try:
                    start_time = datetime.strptime(data.get('start_time'), '%H:%M:%S').time()
                    end_time = datetime.strptime(data.get('end_time'),  '%H:%M:%S').time()
                    if not start_time < end_time:
                        return Response({'status': 'failed', 'error': 'Not valid time to add user'}) 
                    else:
                        obj, created = TimePeriod.objects.update_or_create(
                            user_id=user,defaults={
                                'start_time':data.get('start_time'),
                                'end_time': data.get('end_time')
                            }
                        )
                except ObjectDoesNotExist:
                    return Response({'status': 'failed', 'error': 'Please Set time period'})
            else:
                user.user_permissions.add(permission)
            
            return Response({'status': 'success', 'msg': 'successfully added'})


class PermissionListView(ListAPIView):
    """
    This api will return all permisson for staff user
    """
    serializer_class = PermissionSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Permission.objects.filter(
            Q(codename__startswith='staff')|
            Q(codename__startswith="user"))

