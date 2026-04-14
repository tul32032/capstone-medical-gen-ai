from django.urls import path
from .views import AdminAnalyticsApi

urlpatterns = [
    path("analytics/admin/", AdminAnalyticsApi.as_view(), name="admin-analytics"),
]
