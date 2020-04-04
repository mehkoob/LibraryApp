from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)
from library.views import (
    Login, RegistrationView,BookCreate,
    BookListView, BookDetails, 
    PermissionListView, RequestCreate,
    GrantPermission
)

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('login', Login.as_view(), name='login'),
    path('user/<pk>/', RegistrationView.as_view(), name='user-data'),
    path('user-create/', RegistrationView.as_view(), name='user-create'),
    path('book-create/', BookCreate.as_view(), name='book-create'),
    path('book-list/', BookListView.as_view(), name='book-list'),
    path('book-details/<pk>/', BookDetails.as_view(), name='book-details'),
    path('request-create/', RequestCreate.as_view(), name='request-create'),
    path('permission-list/', PermissionListView.as_view(), name='permission-list'),
    path('permission-add/', GrantPermission.as_view(), name='permission-add'),
]