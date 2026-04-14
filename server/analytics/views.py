import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

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

        total_queries = Query.objects.count()
        total_users = User.objects.count()

        documents = []
        total_documents = 0

        data = {
            "total_queries": total_queries,
            "total_documents": total_documents,
            "total_users": total_users,
            "documents": documents,
        }

        return Response(data)
