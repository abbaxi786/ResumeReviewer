from django.core.files.storage import FileSystemStorage
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from api.util.t1 import (
    CheckRoot,
    AssignAccordingToExt,
    ROLE_KEYWORDS
)


@api_view(["GET", "POST"])
def FileMessage(request):

    if request.method == "GET":
        return Response("Welcome to my app")

    # Get multiple files
    uploaded_files = request.FILES.getlist("files")

    if not uploaded_files:
        return Response(
            {"error": "No files uploaded."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Job description
    description = request.data.get("description", "")

    # Required experience
    requiredExperience = request.data.get("requiredExperience")

    if requiredExperience is None:
        return Response(
            {"error": "requiredExperience is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        requiredExperience = int(requiredExperience)
    except (ValueError, TypeError):
        return Response(
            {"error": "requiredExperience must be an integer."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Role
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

    storage = FileSystemStorage()

    results = []

    # Process every resume
    for uploaded_file in uploaded_files:

        if not CheckRoot(uploaded_file.name):
            results.append({
                "filename": uploaded_file.name,
                "error": "Unsupported file type."
            })
            continue

        try:
            # Save file
            filename = storage.save(
                uploaded_file.name,
                uploaded_file
            )

            # Get path and URL
            file_path = storage.path(filename)
            file_url = storage.url(filename)

            # Analyze resume
            text_info = AssignAccordingToExt(
                file_path,
                requiredExperience,
                role,
                description
            )

            results.append({
                "filename": filename,
                "url": file_url,
                "textInfo": text_info
            })

        except ValueError as e:

            results.append({
                "filename": uploaded_file.name,
                "error": str(e)
            })

        except Exception as e:

            results.append({
                "filename": uploaded_file.name,
                "error": str(e)
            })

        results.sort(
        key=lambda x: x.get("textInfo", {})
                        .get("ResumeScores", {})
                        .get("TotalResumeScore", 0),
        reverse=True
    )

    rank = 1

    for result in results:

        text_info = result.get("textInfo")

        if not text_info:
            continue

        resume_scores = text_info.get("ResumeScores", {})
        description_scores = resume_scores.get("DescriptionScores", {})

        result["ranking"] = {
            "Rank": rank,
            "Name": result.get("filename"),
            "Score": resume_scores.get("TotalResumeScore", 0),
            "MatchPercentage": description_scores.get("skills_scores", 0),
            "TopMissingSkill": (
                description_scores.get("MissingSkills", [None])[0]
                if description_scores.get("MissingSkills")
                else None
            )
        }

        rank += 1
    return Response(
        {
            "message": "Files processed successfully.",
            "total_files": len(uploaded_files),
            "results": results
        },
        status=status.HTTP_201_CREATED,
    )