import requests
from django.http import JsonResponse
from django.views import View

BASE = "http://10.0.1.5/"


class ChatProxyView(View):
    def get(self, request):
        params = request.GET.dict()
        try:
            response = requests.get(BASE, params=params, timeout=30)
            return JsonResponse(response.json(), status=response.status_code)
        except requests.exceptions.RequestException as e:
            return JsonResponse({"error": str(e)}, status=502)
