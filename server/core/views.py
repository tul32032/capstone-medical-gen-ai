import os
import requests
from pdf_processing.upload_ingest import ingest_uploaded_pdf
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

AI_INFRA_BASE_URL = "http://10.0.1.5"
API_KEY = os.environ.get("AI_INFRA_API_KEY", "")
PROJECT_ID = os.environ.get("AI_INFRA_PROJECT_ID", "")

SYSTEM_PROMPT = (
    "You are a endocrinologist with a specialization in diabetes. Your goal is to provide "
    "evidence-based information regarding diabetes as well as diabetes management. Every single "
    "claim must end with a citation in brackets like [Source: DocName, Page #]. If the source is "
    "not in the context, say 'I do not know'.\n\nResponse Structure:\nA brief 1-2 sentence answer.\n"
    "A more detailed explanation giving insights derived from the retrieved context.\n"
    'A "References" section at the bottom.\n\nSafety and Constraints:\nYou cannot prescribe '
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
        if not message:
            return JsonResponse(
                {"error": "Missing required field: message"}, status=400
            )

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
                },
            )
            data = response.json()
            return JsonResponse(
                {
                    "answer": data.get("answer", ""),
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
