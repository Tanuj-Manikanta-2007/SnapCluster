from django.urls import path
from .views import CreateRoom, JoinRoom, RoomImages, UploadImages,UploadZip
urlpatterns = [
  path('upload-images/', UploadImages.as_view()),
  path('upload-zip/',UploadZip.as_view()),
  path('create_room/', CreateRoom.as_view()),
  path('join_room/', JoinRoom.as_view()),
  path('room-images/<str:code>/', RoomImages.as_view()),
]