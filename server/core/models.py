from django.db import models

# Create your models here.
class Session(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_new_add=True)

# Might delete chat table if unnecessary
class Chat(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)

class Question(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    session = modesl.ForeignKey(Session, on_delete=models.CASCADE)
    chat = modesl.ForeignKey(Chat, on_delete=models.CASCADE)
    created_at = models.DATETIMEFIELD(auto_new_add=True)
    question = models.TextField()
    answer = models.TextField()
    citation = models.TextField()
    class Meta:
        ordering = ['created_at']