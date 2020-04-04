from rest_framework.serializers import ModelSerializer
from django.contrib.auth.models import Permission
from library.models import User, RequestBook, Book

class PermissionSerializer(ModelSerializer):
    """ 
    Serializer for permission
    """
    class Meta:
        model = Permission
        fields = '__all__'


class UserSerializer(ModelSerializer):
    """
    Serializer for user
    """
    class Meta:
        model = User
        exclude = ['password']


class BookSerializer(ModelSerializer):
    """
    Serializer for book
    """
    class Meta:
        model = Book
        fields = '__all__'


class RequestBookSerializer(ModelSerializer):
    """
    Serializer for request books
    """
    class Meta:
        model = RequestBook
        fields = '__all__'