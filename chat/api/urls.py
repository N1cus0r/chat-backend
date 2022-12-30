from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView
)

from . import views

urlpatterns = [
    path('register/', views.CreateUser.as_view()),
    path('token/', views.MyTokenObtainPairView.as_view()),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('token/refresh/', TokenRefreshView.as_view()),
    path('get-room-details/', views.GetRoomDetails.as_view()),
    path('create-room/', views.CreateRoom.as_view()),
    path('join-room/', views.JoinRoom.as_view()),
    path('leave-room/', views.LeaveRoom.as_view()),
    path('get-messages/', views.GetRoomMessages.as_view()),
    path('is-room-active/', views.IsRoomActive.as_view()),
]
