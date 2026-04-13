import os
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import timedelta
from django.utils import timezone

from authentication.mixins import ApiAuthMixin
from authentication.backends import JWTCookieAuthentication
from .models import Query, BudgetUsage
from authentication.models import User

AI_INFRA_BASE_URL = os.environ.get("AI_INFRA_BASE_URL", "http://10.0.1.5")
API_KEY = os.environ.get("AI_INFRA_API_KEY", "")
PROJECT_ID = os.environ.get("AI_INFRA_PROJECT_ID", "")


class AdminAnalyticsApi(ApiAuthMixin, APIView):
    authentication_classes = (JWTCookieAuthentication,)

    def get(self, request):
        if not request.user.is_superuser:
            return Response(
                {"error": "Admin access required"}, status=status.HTTP_403_FORBIDDEN
            )

        today = timezone.now().date()
        week_ago = today - timedelta(days=7)

        total_queries = Query.objects.count()
        total_users = User.objects.count()

        recent_queries = Query.objects.filter(created_at__date__gte=week_ago).count()

        try:
            response = requests.get(
                f"{AI_INFRA_BASE_URL}/query/{PROJECT_ID}/documents",
                headers={"Authorization": f"Bearer {API_KEY}"},
                timeout=30,
            )
            documents_data = response.json() if response.ok else {}
        except requests.exceptions.RequestException:
            documents_data = {"documents": []}

        documents = documents_data.get("documents", [])
        total_documents = len(documents)

        budget_data = BudgetUsage.objects.first()
        gcp_budget_used = float(budget_data.gcp_cost_estimate) if budget_data else 0.0

        data = {
            "total_queries": total_queries,
            "total_documents": total_documents,
            "total_users": total_users,
            "gcp_budget_used": gcp_budget_used,
            "recent_queries": recent_queries,
            "documents": documents,
        }

        return Response(data)


class RecordQueryApi(ApiAuthMixin, APIView):
    authentication_classes = (JWTCookieAuthentication,)

    def post(self, request):
        message = request.data.get("message")
        answer = request.data.get("answer")

        if message and answer:
            Query.objects.create(user=request.user, message=message, answer=answer)

            BudgetUsage.objects.update_or_create(
                date=timezone.now().date(),
                defaults={
                    "total_queries": BudgetUsage.objects.filter(
                        date=timezone.now().date()
                    )
                    .first()
                    .total_queries
                    + 1
                    if BudgetUsage.objects.filter(date=timezone.now().date()).exists()
                    else 1
                },
            )

        return Response({"success": True})
