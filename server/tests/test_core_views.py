from types import SimpleNamespace
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
import requests


def test_chat_proxy_rejects_invalid_json(client):
    response = client.post(
        reverse("chat"),
        data="{bad json",
        content_type="application/json",
    )

    assert response.status_code == 400
    assert response.json()["error"] == "Invalid JSON body"


def test_chat_proxy_requires_message(client):
    response = client.post(
        reverse("chat"),
        data="{}",
        content_type="application/json",
    )

    assert response.status_code == 400
    assert response.json()["error"] == "Missing required field: message"


@patch("core.views.requests.post")
def test_chat_proxy_returns_downstream_answer(mock_post, client):
    mock_post.return_value = SimpleNamespace(
        status_code=200,
        json=lambda: {"answer": "Structured answer", "citations": ["Doc A"]},
    )

    response = client.post(
        reverse("chat"),
        data='{"message":"What is diabetes?"}',
        content_type="application/json",
    )

    assert response.status_code == 200
    assert response.json() == {
        "answer": "Structured answer",
        "citations": ["Doc A"],
    }


@patch("core.views.requests.post", side_effect=requests.exceptions.RequestException("infra down"))
def test_chat_proxy_handles_request_exception(mock_post, client):
    response = client.post(
        reverse("chat"),
        data='{"message":"What is diabetes?"}',
        content_type="application/json",
    )

    assert response.status_code == 502
    assert response.json()["error"] == "infra down"


def test_upload_requires_file(client):
    response = client.post(reverse("upload"))

    assert response.status_code == 400
    assert response.json()["error"] == "Missing required field: file"


@patch("core.views.ingest_uploaded_pdf", return_value=None)
def test_upload_returns_500_when_markdown_generation_fails(mock_ingest, client):
    response = client.post(
        reverse("upload"),
        data={"file": SimpleUploadedFile("paper.pdf", b"%PDF-1.7")},
    )

    assert response.status_code == 500
    assert response.json()["error"] == "Failed to process PDF into markdown"


@patch("core.views.requests.put")
@patch("core.views.requests.post")
@patch("core.views.ingest_uploaded_pdf", return_value="# Title\n\nBody")
def test_upload_completes_ingest_flow(mock_ingest, mock_post, mock_put, client):
    init_response = SimpleNamespace(
        status_code=200,
        json=lambda: {"upload_url": "https://upload.example.com", "session_id": "abc123"},
        raise_for_status=lambda: None,
    )
    complete_response = SimpleNamespace(
        status_code=202,
        json=lambda: {"ingested": True},
        raise_for_status=lambda: None,
    )
    mock_post.side_effect = [init_response, complete_response]
    mock_put.return_value = SimpleNamespace(raise_for_status=lambda: None)

    response = client.post(
        reverse("upload"),
        data={"file": SimpleUploadedFile("paper.pdf", b"%PDF-1.7")},
    )

    assert response.status_code == 202
    assert response.json() == {
        "success": True,
        "status": 202,
        "infra_response": {"ingested": True},
    }


@patch("core.views.requests.post", side_effect=requests.exceptions.RequestException("upload failed"))
@patch("core.views.ingest_uploaded_pdf", return_value="# Title\n\nBody")
def test_upload_handles_request_exception(mock_ingest, mock_post, client):
    response = client.post(
        reverse("upload"),
        data={"file": SimpleUploadedFile("paper.pdf", b"%PDF-1.7")},
    )

    assert response.status_code == 502
    assert response.json()["error"] == "upload failed"
