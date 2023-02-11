from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from . import views


app_name = "chat"

urlpatterns = [
    path("register/", views.CreateUser.as_view(), name="create-user"),
    path("token/", views.MyTokenObtainPairView.as_view()),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("token/refresh/", TokenRefreshView.as_view()),
    path("get-room-details/", views.GetRoomDetails.as_view(), name="get-room-details"),
    path("create-room/", views.CreateRoom.as_view(), name="create-room"),
    path("join-room/", views.JoinRoom.as_view(), name="join-room"),
    path("leave-room/", views.LeaveRoom.as_view(), name="leave-room"),
    path("get-messages/", views.GetRoomMessages.as_view(), name="get-messages"),
    path("is-room-active/", views.IsRoomActive.as_view(), name="is-room-active"),
]
