from django.test import TestCase
# Create your tests here.
# Using the standard RequestFactory API to create a form POST request
from rest_framework.test import APIRequestFactory, force_authenticate
from library.models import User, Book


factory = APIRequestFactory()


request = factory.post('/api/book-create/',  {
    "title":"Balyakala Sakhi", 
    "author": "Basheer", 
    "book_code": "bbcode0001",
    "total_copies" :"12",
    "available_copies":"7"}, format='json')

print("test book create result", request)

# class BookTestCase(TestCase):
#     fixtures = ['book.json']

#     def setUp(self):
#         # Test definitions as before.
#         call_setup_methods()

#     def testFluffyAnimals(self):
#         # A test that uses the fixtures.
#         call_some_test_code()
