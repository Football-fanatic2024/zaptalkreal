import re
from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Message, GroupMessage

def safe_group_name(name: str) -> str:
    return re.sub(r'[^a-zA-Z0-9_.-]', '_', name)

@receiver(post_save, sender=Message)
def broadcast_direct_message(sender, instance, created, **kwargs):
    if not created:
        return
    channel_layer = get_channel_layer()
    room_group = f"chat_{safe_group_name(min(instance.sender.username, instance.receiver.username))}_{safe_group_name(max(instance.sender.username, instance.receiver.username))}"
    async_to_sync(channel_layer.group_send)(
        room_group,
        {
            "type": "chat_message",
            "sender": instance.sender.username,
            "text": instance.text,
            "timestamp": str(instance.timestamp),
        }
    )

@receiver(post_save, sender=GroupMessage)
def broadcast_group_message(sender, instance, created, **kwargs):
    if not created:
        return
    channel_layer = get_channel_layer()
    room_group = f"group_{safe_group_name(str(instance.group.id))}"
    async_to_sync(channel_layer.group_send)(
        room_group,
        {
            "type": "chat_message",
            "sender": instance.sender.username,
            "text": instance.text,
            "timestamp": str(instance.timestamp),
        }
    )
