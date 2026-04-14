import os
import requests
from pdf_processing.upload_ingest import ingest_uploaded_pdf
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
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
        if not message:
            return JsonResponse(
                {"error": "Missing required field: message"}, status=400
            )

        user = request.user

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
                    "min_score": 0.5,
                },
            )
            data = response.json()
            answer = data.get("answer", "")

            Query.objects.create(
                user=user,
                message=message,
                answer=answer,
            )

            return JsonResponse(
                {
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
                    "message": "Infra accepted upload for processing"
                    if complete_response.status_code == 202
                    else "Upload successful",
                    "infra_response": complete_response.json(),
                },
                status=complete_response.status_code,
            )
        except requests.exceptions.RequestException as e:
            return JsonResponse({"error": str(e)}, status=502)
