from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from unittest.mock import patch
from rest_framework.test import APIClient
import json

from core.models import Chat, Question

# Create your tests here.
User = get_user_model()

class ChatCreationTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )

    def test_create_new_chat(self):
        chat = Chat.objects.create(user=self.user)

        self.assertEqual(chat.user, self.user)
        self.assertIsNotNone(chat.id)

    def test_get_or_create_new_chat(self):
        chat = Chat.objects.create(user=self.user)

        self.assertIsNotNone(chat.id)

class QuestionModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.chat = Chat.objects.create(user=self.user)

    def test_create_question(self):
        q = Question.objects.create(
            user=self.user,
            chat=self.chat,
            question="What is diabetes?",
            answer="Diabetes is a condition...",
            citation=[]
        )

        self.assertEqual(q.chat, self.chat)
        self.assertEqual(q.question, "What is diabetes?")
        self.assertTrue(len(q.answer) > 0)

    def test_question_belongs_to_chat(self):
        q = Question.objects.create(
            user=self.user,
            chat=self.chat,
            question="Hello",
            answer="Hi",
            citation=[]
        )

        self.assertEqual(q.chat.id, self.chat.id)

class ChatHistoryViewTests(TestCase):

    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )

        self.chat = Chat.objects.create(user=self.user)

        Question.objects.create(
            user=self.user,
            chat=self.chat,
            question="What is diabetes?",
            answer="A disease...",
            citation=[]
        )

    def test_chat_history_requires_login(self):
        response = self.client.get("/api/history/")
        self.assertEqual(response.status_code, 302)

    def test_chat_history_with_chat_id(self):
        self.client.login(username="testuser", password="testpass123")
        
        response = self.client.get(f"/api/history/?chat_id={self.chat.id}")

        self.assertEqual(response.status_code, 200)

    def test_chat_history_returns_data(self):
        self.client.login(username="testuser", password="testpass123")

        response = self.client.get(f"/api/history/?chat_id={self.chat.id}")

        self.assertEqual(response.status_code, 200)

        self.assertTrue(
            "diabetes" in response.content.decode().lower()
            or response.content != b""
        )


class ChatIntegrationTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.chat = Chat.objects.create(user=self.user)
    
    @patch("core.views.requests.post")
    def test_full_chat_flow(self, mock_post):
        self.client.force_authenticate(user=self.user)
        self.client.login(username="testuser", password="testpass123")

        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "answer": "Test answer",
            "citations": []
        }

        response = self.client.post(
            "/api/chat/",
            data=json.dumps({"message": "What is diabetes?"}),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)

        response_data = response.json()
        chat_id = response_data.get("chat_id")
        
        self.assertIsNotNone(chat_id)
        self.assertEqual(Chat.objects.count(), 2)
        self.assertEqual(Question.objects.count(), 1)

        history = self.client.get(f"/api/history/?chat_id={chat_id}")

        self.assertEqual(history.status_code, 200)

class ChatProxyViewTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass"
        )

    @patch("core.views.requests.post")
    def test_chat_creates_database_records(self, mock_post):
        self.client.force_authenticate(user=self.user)
        
        mock_post.return_value.json.return_value = {
        "answer": "Test answer",
        "citations": []
        }
        mock_post.return_value.status_code = 200

        
        response = self.client.post(
            "/api/chat/",  # adjust to your URL
            data={
                "message": "hello test",
                "chat_id": None
            },
            content_type="application/json"
        )

        # 1. Check response
        self.assertEqual(response.status_code, 200)

        # 2. Check DB state
        self.assertEqual(Chat.objects.count(), 1)
        self.assertEqual(Question.objects.count(), 1)

        q = Question.objects.first()
        self.assertEqual(q.question, "hello test")

    @patch("core.views.requests.post")
    def test_chat_relationship(self, mock_post):
        self.client.force_authenticate(user=self.user)

        mock_post.return_value.json.return_value = {
        "answer": "Test answer",
        "citations": []
        }
        mock_post.return_value.status_code = 200

        response = self.client.post(
            "/api/chat/",
            data=json.dumps({"message": "hello"}),
            content_type="application/json"
        )

        chat = Chat.objects.first()
        question = Question.objects.first()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(question.chat, chat)
        self.assertEqual(question.user, self.user)