from django.urls import path
from .views import RegisterView,UpdatePasswordView,VerifyTokenView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
   path('register',RegisterView.as_view()),
   path('login',TokenObtainPairView.as_view()),
   path('refresh',TokenRefreshView.as_view()),
   path('update-password',UpdatePasswordView.as_view()),
   path('verify',VerifyTokenView.as_view()),
]
