from django.urls import path

from .views import (
    LoginView,
    LogoutView,
    MeView,
    MySettingsView,
    RefreshView,
    RegisterView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('refresh/', RefreshView.as_view(), name='refresh'),
    path('me/', MeView.as_view(), name='me'),
    path('me/settings/', MySettingsView.as_view(), name='my-settings'),
]
