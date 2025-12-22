from django.db import models
from django.contrib.auth.models import User

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages")
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} → {self.receiver.username}: {self.text[:20]}"


class Group(models.Model):
    name = models.CharField(max_length=100)
    # FIX: give members a unique related_name so it doesn’t clash with auth.User.groups
    members = models.ManyToManyField(User, related_name="chat_groups")

    def __str__(self):
        return self.name


class GroupMessage(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="group_messages")
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} in {self.group.name}: {self.text[:20]}"
