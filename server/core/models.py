from django.db import models
from django.conf import settings

# Create your models here.

class Chat(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class Question(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    question = models.TextField()
    answer = models.TextField()
    citation = models.JSONField()
    class Meta:
        ordering = ['created_at']