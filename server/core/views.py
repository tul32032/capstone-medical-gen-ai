import requests
from django.http import JsonResponse
from django.views import View

AI_SERVICE_URL = "https://api-service-703116401106.us-east1.run.app/"


class ChatProxyView(View):
    def get(self, request):
        params = request.GET.dict()
        try:
            response = requests.get(AI_SERVICE_URL, params=params, timeout=30)
            return JsonResponse(response.json(), status=response.status_code)
        except requests.exceptions.RequestException as e:
            return JsonResponse({"error": str(e)}, status=502)
