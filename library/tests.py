from django.test import TestCase

# Create your tests here.
# Using the standard RequestFactory API to create a form POST request
from rest_framework.test import APIRequestFactory, force_authenticate
from library.models import User
from library.views import RegistrationView


factory = APIRequestFactory()


request = factory.post('/api/book-create/',  {
    "title":"Balyakala Sakhi", 
    "author": "Basheer", 
    "book_code": "bbcode0001",
    "total_copies" :"12",
    "available_copies":"7"}, format='json')

print("test book create result", request)


user = User.objects.get(username='olivia')
view = RegistrationView.as_view()

# Make an authenticated request to the view...
request1 = factory.get('/accounts/django-superstars/')
force_authenticate(request1, user=user)
response = view(request1)