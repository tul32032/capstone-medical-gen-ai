from django.db import models
from django.conf import settings

# Create your models here.

# Might delete chat table if unnecessary
#class Session(models.Model):
#    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#    created_at = models.DateTimeField(auto_now_add=True)

class Chat(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    #session = models.ForeignKey(Session, on_delete=models.CASCADE)
    chat_number = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('user', 'chat_number')

class Question(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    #session = models.ForeignKey(Session, on_delete=models.CASCADE)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    question = models.TextField()
    answer = models.TextField()
    citation = models.TextField()
    class Meta:
        ordering = ['created_at']