from django.urls import reverse
from django.utils import timezone

from analytics.models import Query
from authentication.models import User
from tests.helpers import attach_access_cookie


def test_admin_analytics_rejects_non_admin_user(client):
    user = User.objects.create_user(
        username="basic",
        email="basic@example.com",
        password="password123",
    )
    attach_access_cookie(client, user)

    response = client.get(reverse("admin-analytics"))

    assert response.status_code == 403
    assert response.json()["error"] == "Admin access required"


def test_admin_analytics_returns_summary_for_superuser(client):
    admin_user = User.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="password123",
    )
    other_user = User.objects.create_user(
        username="member",
        email="member@example.com",
        password="password123",
    )
    attach_access_cookie(client, admin_user)

    recent_query = Query.objects.create(
        user=other_user,
        message="Recent question",
        answer="Recent answer",
    )
    Query.objects.filter(id=recent_query.id).update(created_at=timezone.now())

    response = client.get(reverse("admin-analytics"))
    payload = response.json()

    assert response.status_code == 200
    assert payload["total_queries"] == 1
    assert payload["total_users"] == 2
    assert payload["recent_queries"] == 1
    assert payload["documents"] == []


def test_record_query_creates_row_when_message_and_answer_exist(client):
    user = User.objects.create_user(
        username="writer",
        email="writer@example.com",
        password="password123",
    )
    attach_access_cookie(client, user)

    response = client.post(
        reverse("record-query"),
        data={"message": "How are you?", "answer": "I am fine."},
        content_type="application/json",
    )

    assert response.status_code == 200
    assert response.json() == {"success": True}
    assert Query.objects.count() == 1


def test_record_query_skips_creation_when_payload_is_incomplete(client):
    user = User.objects.create_user(
        username="partial",
        email="partial@example.com",
        password="password123",
    )
    attach_access_cookie(client, user)

    response = client.post(
        reverse("record-query"),
        data={"message": "Missing answer"},
        content_type="application/json",
    )

    assert response.status_code == 200
    assert Query.objects.count() == 0
