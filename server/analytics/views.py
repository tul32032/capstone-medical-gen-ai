import os
import requests
from google.cloud import bigquery
from google.api_core.exceptions import GoogleAPIError

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from authentication.mixins import ApiAuthMixin
from authentication.backends import JWTCookieAuthentication
from .models import Query
from authentication.models import User

AI_INFRA_BASE_URL = "http://10.0.1.5"
API_KEY = os.environ.get("AI_INFRA_API_KEY", "")
PROJECT_ID = os.environ.get("AI_INFRA_PROJECT_ID", "")

GCP_PROJECT_ID = "capstone-med-product"
GCP_DATASET = "checkbilling"


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

        try:
            response = requests.get(
                f"{AI_INFRA_BASE_URL}/query/{PROJECT_ID}/documents",
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json",
                },
                timeout=10,
            )

            response.raise_for_status()
            data = response.json()

            if isinstance(data, list):
                documents = data
                total_documents = len(data)

        except (requests.RequestException, ValueError) as e:
            pass

        total_cost = 26.06
        try:
            client = bigquery.Client(project=GCP_PROJECT_ID)

            query = f"""
            SELECT SUM(cost) AS total_cost
            FROM `{GCP_PROJECT_ID}.{GCP_DATASET}.gcp_billing_export_v1_*`
            """

            result = client.query(query).result()

            for row in result:
                if row.total_cost is not None:
                    total_cost += float(row.total_cost)

        except (GoogleAPIError, Exception):
            pass

        return Response(
            {
                "total_queries": total_queries,
                "total_documents": total_documents,
                "total_users": total_users,
                "documents": documents,
                "total_cost": total_cost,
            }
        )
