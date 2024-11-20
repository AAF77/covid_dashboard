from django.urls import path
from .views import LoginView, AccountDetailView, ChangePasswordView, RegistrationView, LogoutView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegistrationView.as_view(), name='register'),
    path('account/', AccountDetailView.as_view(), name='account'),
    path('account/change-password/', ChangePasswordView.as_view(), name='change_password'),
]
