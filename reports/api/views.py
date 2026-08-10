from django.core.files.storage import FileSystemStorage
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User

from api.util.t1 import (
    CheckRoot,
    AssignAccordingToExt,
    ROLE_KEYWORDS
)

from .models import ResumeResult


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def FileMessage(request):
    
    if request.method == "GET":

        user = request.user

        data = ResumeResult.objects.filter(user=user).values(
            "id",
            "filename",
            "url",
            "role",
            "description",
            "required_experience",
            "text_info",
            "rank",
            "score",
            "match_percentage",
            "top_missing_skill",
            "error",
            "created_at"
        )

        return Response({
            "data": list(data)
        })


    
    uploaded_files = request.FILES.getlist("files")

    if not uploaded_files:
        return Response(
            {"error": "No files uploaded."},
            status=status.HTTP_400_BAD_REQUEST,
        )


    
    description = request.data.get("description", "")


    
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


    
    for uploaded_file in uploaded_files:

        
        if not CheckRoot(uploaded_file.name):

            results.append({
                "filename": uploaded_file.name,
                "error": "Unsupported file type."
            })

            continue


        try:

            
            filename = storage.save(
                uploaded_file.name,
                uploaded_file
            )

            file_path = storage.path(filename)

            file_url = storage.url(filename)


            
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

        score = resume_scores.get("TotalResumeScore", 0)
        match_percentage = description_scores.get("skills_scores", 0)

        missing_skills = description_scores.get("MissingSkills", [])
        top_missing_skill = (missing_skills[0] if missing_skills else None)
        result["ranking"] = {
            "Rank": rank,
            "Name": result.get("filename"),
            "Score": score,
            "MatchPercentage": match_percentage,
            "TopMissingSkill": top_missing_skill
        }


        
        ResumeResult.objects.create(
            user=request.user,

            filename=result.get("filename"),

            file=result.get("filename"),

            url=result.get("url"),

            role=role,

            description=description,

            required_experience=requiredExperience,

            text_info=text_info,

            rank=rank,

            score=score,

            match_percentage=match_percentage,

            top_missing_skill=top_missing_skill,

            error=None
        )


        rank += 1


    # ==========================================
    # Response
    # ==========================================

    return Response(
        {
            "message": "Files processed successfully.",
            "total_files": len(uploaded_files),
            "results": results
        },
        status=status.HTTP_201_CREATED,
    )

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def GetSingleResume(request, resume_id):
    try:
        if request.method == "GET":
            user = request.user

            if not resume_id:
                return Response(
                    {"error": "resume_id is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                resume_result = ResumeResult.objects.get(
                    id=resume_id, user=user
                )
            except ResumeResult.DoesNotExist:
                return Response(
                    {"error": "Resume not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            data = {
                "filename": resume_result.filename,
                "url": resume_result.url,
                "role": resume_result.role,
                "description": resume_result.description,
                "required_experience": resume_result.required_experience,
                "text_info": resume_result.text_info,
                "rank": resume_result.rank,
                "score": resume_result.score,
                "match_percentage": resume_result.match_percentage,
                "top_missing_skill": resume_result.top_missing_skill,
                "error": resume_result.error,
                "created_at": resume_result.created_at
            }

            return Response({"data": data}, status=status.HTTP_200_OK)
    except Exception as error:
        print(error)