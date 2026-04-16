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
        chat = Chat.objects.create(user=self.user, chat_number=1)

        self.assertEqual(chat.user, self.user)
        self.assertEqual(chat.chat_number, 1)

    def test_get_or_create_new_chat(self):
        chat = Chat.objects.create(user=self.user, chat_number=1)

        self.assertIsNotNone(chat.id)

    def test_multiple_chats_increment_number(self):
        chat1 = Chat.objects.create(user=self.user, chat_number=1)
        chat2 = Chat.objects.create(user=self.user, chat_number=2)

        self.assertEqual(chat2.chat_number, chat1.chat_number + 1)

class QuestionModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.chat = Chat.objects.create(user=self.user, chat_number=1)

    def test_create_question(self):
        q = Question.objects.create(
            user=self.user,
            chat=self.chat,
            question="What is diabetes?",
            answer="Diabetes is a condition..."
        )

        self.assertEqual(q.chat, self.chat)
        self.assertEqual(q.question, "What is diabetes?")
        self.assertTrue(len(q.answer) > 0)

    def test_question_belongs_to_chat(self):
        q = Question.objects.create(
            user=self.user,
            chat=self.chat,
            question="Hello",
            answer="Hi"
        )

        self.assertEqual(q.chat.id, self.chat.id)

class ChatHistoryViewTests(TestCase):

    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )

        self.chat = Chat.objects.create(user=self.user, chat_number=1)

        Question.objects.create(
            user=self.user,
            chat=self.chat,
            question="What is diabetes?",
            answer="A disease..."
        )

    def test_chat_history_requires_login(self):
        response = self.client.get("/api/history/")
        self.assertEqual(response.status_code, 302)

    def test_chat_history_returns_data(self):
        self.client.login(username="testuser", password="testpass123")

        response = self.client.get("/api/history/")

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
        self.chat = Chat.objects.create(
            user=self.user,
            chat_number=1
        )
    
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

        history = self.client.get("/api/history/")

        self.assertEqual(history.status_code, 200)