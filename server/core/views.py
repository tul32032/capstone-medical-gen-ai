import os
import requests
import json
from pdf_processing.upload_ingest import ingest_uploaded_pdf
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Chat, Question
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from authentication.backends import JWTCookieAuthentication
from authentication.models import User
from analytics.models import Query

AI_INFRA_BASE_URL = "http://10.0.1.5"
API_KEY = os.environ.get("AI_INFRA_API_KEY", "")
PROJECT_ID = os.environ.get("AI_INFRA_PROJECT_ID", "")

SYSTEM_PROMPT = (
    "You are a endocrinologist with a specialization in diabetes. Your goal is to provide "
    "evidence-based information regarding diabetes as well as diabetes management. Every single "
    "claim must end with a citation in brackets like [Source: DocName, Page #]. If the source is "
    "not in the context, do not respond to the question.\n\nResponse Structure:\nFirst give a brief 1-2 sentence answer.\n"
    "Then give a more detailed explanation giving insights derived from the retrieved context.\n"
    'Finally give a "References" section at the bottom.\n\nSafety and Constraints:\nYou cannot prescribe '
    "specific dosages for medications. You may discuss standard ranges but must direct the user to "
    "their healthcare provider.\nBe professional and clear, avoid overly dense medical jargon unless "
    "explaining it.\nStrictly limit your answer to the provided context. Do not use outside knowledge."
)


@method_decorator(csrf_exempt, name="dispatch")
class ChatProxyView(View):
    def post(self, request):
        import json

        try:
            body = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({"error": "Invalid JSON body"}, status=400)

        message = body.get("message")
        chat_id = body.get("chat_id")

        if not message:
            return JsonResponse(
                {"error": "Missing required field: message"}, status=400
            )

        user = None
        auth_result = request.user
        if isinstance(auth_result, tuple):
            user = auth_result[0]
        elif hasattr(request, "user") and request.user.is_authenticated:
            user = request.user

        User = request.user
        chat_id = get_or_create_chat(User, chat_id)

        try:
            response = requests.post(
                f"{AI_INFRA_BASE_URL}/api/v1/chat",
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "question": message,
                    "project_id": PROJECT_ID,
                    "system_prompt": SYSTEM_PROMPT,
                    "min_score": 0.8,
                },
            )
            data = response.json()
            answer = data.get("answer", "")
            citations = data.get("citations", [])

            if user:
                Query.objects.create(
                    user=user,
                    message=message,
                    answer=answer,
                )

            Question.objects.create(
                user=User,
                chat=chat_id,
                question=message,
                answer=answer,
                citation=str(citations)
            )   
            
            return JsonResponse(
                {
                    "answer": data.get("answer", ""),
                    "citations": data.get("citations", []),
                },
                status=response.status_code
            )

        except requests.exceptions.RequestException as e:
            return JsonResponse({"error": str(e)}, status=502)


@method_decorator(csrf_exempt, name="dispatch")
class UploadFile(View):
    def post(self, request):
        file = request.FILES.get("file")
        if not file:
            return JsonResponse({"error": "Missing required field: file"}, status=400)

        md_text = ingest_uploaded_pdf(file)
        if not md_text:
            return JsonResponse({"error": "Failed to process PDF into markdown"}, status=500)

        try:
            filename = f"{os.path.splitext(file.name)[0]}.md"
            response = requests.post(
                f"{AI_INFRA_BASE_URL}/ingest/{PROJECT_ID}/upload",
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                },
                files={"file": (filename, md_text.encode("utf-8"), "text/markdown")},
            )
            return JsonResponse(
                {
                    "success": response.status_code in (200, 201),
                    "status": response.status_code,
                    "infra_response": response.json(),
                },
                status=response.status_code,
            )
        except requests.exceptions.RequestException as e:
            return JsonResponse({"error": str(e)}, status=502)


def get_or_create_chat(user, chat_id=None):
    if chat_id:
        return Chat.objects.get(id=chat_id, user=user)

    last_chat = Chat.objects.filter(user=user).order_by('-chat_number').first()

    if last_chat and not last_chat.question_set.exists():
        return last_chat

    next_number = 1 if not last_chat else last_chat.chat_number + 1

    return Chat.objects.create(
        user=user,
        chat_number=next_number
    )


@method_decorator(csrf_exempt, name="dispatch")
class ChatHistoryView(LoginRequiredMixin, View):
    def get(self, request, chat_number):
        user = request.user

        chat = Chat.objects.filter(user=user, chat_number=chat_number).first()
        if not chat:
            return JsonResponse({
            "error": "Chat not found",
            "chat_number": chat_number
        }, status=404)

        questions = Question.objects.filter(
            user=user,
            chat=chat
        ).order_by('created_at')

        data = []
        for q in questions:
            data.append({
                "question": q.question,
                "answer": q.answer,
                "citation": q.citation,
                "timestamp": q.created_at.isoformat()
            })

        return JsonResponse({
            "chat_number": chat.chat_number,
            "chat": data
        }, status=200)