from django.db import models

class Conversation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    role = models.CharField(max_length=10, choices=[('user', 'User'), ('assistant', 'Assistant')])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']