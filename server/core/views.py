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
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from authentication.backends import JWTCookieAuthentication
from authentication.models import User
from analytics.models import Query

AI_INFRA_BASE_URL = "http://10.0.1.5"
API_KEY = os.environ.get("AI_INFRA_API_KEY", "")
PROJECT_ID = os.environ.get("AI_INFRA_PROJECT_ID", "")

SYSTEM_PROMPT = (
    "You are an endocrinologist specializing in diabetes. Your goal is to provide "
    "evidence-based information using ONLY the provided context.\n\n"

    "Citation Rules:\n"
    "- Every factual claim MUST end with a citation in this format: [#, p.#]\n"
    "- # = reference number assigned in order of appearance\n"
    "- p.# = page number from the source\n"
    "- Do NOT include document names anywhere in the citation\n\n"

    "Response Structure:\n"
    "1. Provide a brief 1–2 sentence answer.\n"
    "2. Provide a detailed explanation using only the context.\n"
    "3. Provide a References section formatted EXACTLY like:\n"
    "   References:\n"
    "   [1]\n"
    "   [2]\n\n"

    "Safety Constraints:\n"
    "- Do NOT prescribe specific medication dosages.\n"
    "- You may discuss general ranges but must direct users to their healthcare provider.\n"
    "- Be clear and professional.\n"
    "- Use ONLY the provided context. Do NOT use outside knowledge."
)


class ChatProxyView(APIView):
    authentication_classes = (JWTCookieAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        import json

        try:
            body = json.loads(request.body)
        except json.JSONDecodeError, ValueError:
            return JsonResponse({"error": "Invalid JSON body"}, status=400)

        message = body.get("message")
        chat_id = body.get("chat_id")

        if not message:
            return JsonResponse(
                {"error": "Missing required field: message"}, status=400
            )

        user = request.user

        if chat_id:
            chat = Chat.objects.filter(user=user, id=chat_id).first()
            if not chat:
                chat = Chat.objects.create(user=user)
        else:
            chat = Chat.objects.create(user=user)

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
                    "min_score": 0.4,
                },
            )
            data = response.json()
            answer = data.get("answer", "")
            citations = data.get("citations", [])

            Query.objects.create(
                user=user,
                message=message,
                answer=answer,
            )

            Question.objects.create(
                user=user,
                chat=chat,
                question=message,
                answer=answer,
                citation=citations,
            )

            return JsonResponse(
                {
                    "chat_id": chat.id,
                    "answer": answer,
                    "citations": data.get("citations", []),
                },
                status=response.status_code,
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
            return JsonResponse(
                {"error": "Failed to process PDF into markdown"}, status=500
            )

        try:
            filename = f"{os.path.splitext(file.name)[0]}.md"

            init_response = requests.post(
                f"{AI_INFRA_BASE_URL}/ingest/{PROJECT_ID}/upload/init",
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "filename": filename,
                    "content_type": "text/markdown",
                },
            )
            init_response.raise_for_status()
            init_data = init_response.json()

            upload_url = init_data["upload_url"]
            session_id = init_data["session_id"]

            put_response = requests.put(
                upload_url,
                data=md_text.encode("utf-8"),
                headers={"Content-Type": "text/markdown"},
            )
            put_response.raise_for_status()

            complete_response = requests.post(
                f"{AI_INFRA_BASE_URL}/ingest/{PROJECT_ID}/upload/{session_id}/complete",
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                },
            )
            complete_response.raise_for_status()

            return JsonResponse(
                {
                    "success": complete_response.status_code in (200, 201, 202),
                    "status": complete_response.status_code,
                    "message": (
                        "Infra accepted upload for processing"
                        if complete_response.status_code == 202
                        else "Upload successful"
                    ),
                    "infra_response": complete_response.json(),
                },
                status=complete_response.status_code,
            )
        except requests.exceptions.RequestException as e:
            return JsonResponse({"error": str(e)}, status=502)


@method_decorator(csrf_exempt, name="dispatch")
class ChatHistoryView(APIView):
    authentication_classes = (JWTCookieAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user

        chat_id = request.GET.get("chat_id")

        if not chat_id:
            chats = Chat.objects.filter(user=user).order_by("-created_at")
            data = []
            for chat in chats:
                first_question = (
                    Question.objects.filter(chat=chat).order_by("created_at").first()
                )
                data.append(
                    {
                        "id": chat.id,
                        "prompt": (
                            first_question.question if first_question else "New Chat"
                        ),
                        "created_at": chat.created_at.isoformat(),
                    }
                )
            return JsonResponse({"chats": data}, status=200)

        chat = Chat.objects.filter(user=user, id=chat_id).first()

        if not chat:
            return JsonResponse(
                {"error": "Chat not found", "chat_id": chat_id}, status=404
            )

        questions = Question.objects.filter(user=user, chat=chat).order_by("created_at")

        data = []
        for q in questions:
            data.append(
                {
                    "question": q.question,
                    "answer": q.answer,
                    "citation": q.citation,
                    "timestamp": q.created_at.isoformat(),
                }
            )

        return JsonResponse({"chat_id": chat.id, "chat": data}, status=200)
