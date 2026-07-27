from django.core.files.storage import FileSystemStorage
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import json

from api.util.t1 import CheckRoot, AssignAccordingToExt, ROLE_KEYWORDS


@api_view(["GET", "POST"])
def FileMessage(request):

    if request.method == "GET":
        return Response("Welcome to my app")
    
    if request.method== "POST":

        if "file" not in request.FILES:
            return Response(
                {"error": "No file uploaded."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        requiredExperience = request.data.get("requiredExperience")

        if requiredExperience is None:
            return Response(
                {"error": "requiredExperience is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            requiredExperience = int(requiredExperience)
        except ValueError:
            return Response(
                {"error": "requiredExperience must be an integer."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        role = request.data.get("role")

        if not role:
            return Response(
                {"error": "role is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        role = role.strip().lower()


        if role not in ROLE_KEYWORDS:
            return Response(
                {
                    "error": "Unsupported role.",
                    "available_roles": list(ROLE_KEYWORDS.keys())
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


        uploaded_file = request.FILES["file"]

        if not CheckRoot(uploaded_file.name):
            return Response(
                {"error": "Unsupported file type."},
                status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            )

        storage = FileSystemStorage()

        filename = storage.save(uploaded_file.name, uploaded_file)

        file_path = storage.path(filename)
        file_url = storage.url(filename)

        try:
            text_info = AssignAccordingToExt(file_path,requiredExperience,role)
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {
                "message": "File uploaded successfully.",
                "filename": filename,
                "url": file_url,
                "textInfo": text_info,
            },
            status=status.HTTP_201_CREATED,
        )