from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import uuid
import zipfile,io
from .models import Image, Room
from .supabase_client import supabase
from .utils import generate_room_code


class UploadImages(APIView):

  def post(self,request):
    files = request.FILES.get('images')
    room_code = request.data.get('room_code')

    if not files or not room_code:
      return Response({"error" : "Missing data" },status = 400)
    
    try:
      room = Room.objects.get(code=room_code)
    except Room.DoesNotExist:
      return Response({"error" : "Invalid room"},status = 404)
    
    uploaded_urls = []

    for file in files :
      
      file_name = f"{uuid.uuid4()}_{file.name}"
      
      file_path = f"{room.code}/{file_name}"

      file_bytes = file.read()

      supabase.storage.from_("images").upload(file_path, file_bytes)

      public_url = supabase.storage.from_("images").get_public_url(file_path)

      Image.objects.create(
          room=room,
          image_url=public_url
      )

      uploaded_urls.append(public_url)
      return Response({
              "message": "Images successfully",
              "count" : len(uploaded_urls),
              "url": uploaded_urls
          },status=201)


class CreateRoom(APIView):

  def post(self,request):
    name = request.data.get("name")
    code = generate_room_code()

    while Room.objects.filter(code=code).exists():
      code = generate_room_code()

    room = Room.objects.create(
      name=name,
      code=code
    )

    return Response({
      "message": "Room created",
      "room_code": room.code
    }, status=201)


class JoinRoom(APIView):

  def post(self,request):
    code = request.data.get("code")

    try:
      room = Room.objects.get(code=code)
      return Response({
        "message": "Joined",
        "room_name": room.name
      })
    except Room.DoesNotExist:
      return Response({
        "error": "Room not found"
      }, status=404)


class RoomImages(APIView):

  def get(self,request,code):
    try:
      room = Room.objects.get(code=code)
      images = Image.objects.filter(room=room)

      data = [img.image_url for img in images]

      return Response({"images": data})
    except Room.DoesNotExist:
      return Response({"error": "Room not found"}, status=404)


class UploadZip(APIView):

  def post(self,request):
    room_code = request.data.get('room_code')
    zip_file = request.FILES.get('zip_file')

    if not room_code or not zip_file:
      return Response({"error" : "Missing data"},status = 400)

    try:
      room = Room.objects.get(code = room_code)
    except Room.DoesNotExist:
      return Response({"error": "Invalid room"}, status=404)
    
    uploaded_urls = []
    try:
        zip_bytes = zip_file.read()
        zip_data = zipfile.ZipFile(io.BytesIO(zip_bytes))
    except:
        return Response({"error": "Invalid ZIP file"}, status=400)

    for zip_info in zip_data.infolist():

        if zip_info.is_dir():
            continue

        file_name = zip_info.filename

        if not file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
            continue

        import uuid
        file_name = f"{uuid.uuid4()}_{file_name}"

        file_data = zip_data.read(zip_info)

        file_path = f"{room.code}/{file_name}"

        supabase.storage.from_("images").upload(file_path, file_data)

        public_url = supabase.storage.from_("images").get_public_url(file_path)

        Image.objects.create(
            room=room,
            image_url=public_url
        )

        uploaded_urls.append(public_url)

    return Response({
        "message": "ZIP processed successfully",
        "count": len(uploaded_urls),
        "urls": uploaded_urls
    }, status=201)    



