import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import timedelta
from django.utils import timezone

from authentication.mixins import ApiAuthMixin
from authentication.backends import JWTCookieAuthentication
from .models import Query
from authentication.models import User


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

        documents = []
        total_documents = 0

        data = {
            "total_queries": total_queries,
            "total_documents": total_documents,
            "total_users": total_users,
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

        return Response({"success": True})
