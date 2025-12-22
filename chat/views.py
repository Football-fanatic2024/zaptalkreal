from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm
from chat.models import Message, Group, GroupMessage

# ⭐ NEW IMPORTS FOR REAL-TIME BROADCASTING
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone


@login_required
def inbox(request):
    messages = Message.objects.filter(receiver=request.user) | Message.objects.filter(sender=request.user)
    groups = request.user.chat_groups.all()
    return render(request, "inbox.html", {
        "messages": messages.order_by("-timestamp"),
        "groups": groups,
    })


@login_required
def chatroom(request, username):
    other_user = get_object_or_404(User, username=username)

    if request.method == "POST":
        text = request.POST.get("text")
        if text:
            # Save message to DB
            Message.objects.create(sender=request.user, receiver=other_user, text=text)

            # ⭐ REAL-TIME BROADCAST
            room_group = (
                f"chat_{min(request.user.username, other_user.username)}_"
                f"{max(request.user.username, other_user.username)}"
            )

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                room_group,
                {
                    "type": "chat_message",
                    "sender": request.user.username,
                    "text": text,
                    "timestamp": timezone.now().strftime("%b. %d, %Y, %-I:%M %p"),
                }
            )

        return redirect("chatroom", username=other_user.username)

    messages = Message.objects.filter(
        sender=request.user, receiver=other_user
    ) | Message.objects.filter(
        sender=other_user, receiver=request.user
    )

    return render(request, "chatroom.html", {
        "messages": messages.order_by("timestamp"),
        "other_user": other_user,
    })


@login_required
def group_chatroom(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    if request.method == "POST":
        text = request.POST.get("text")
        if text:
            GroupMessage.objects.create(group=group, sender=request.user, text=text)

            # ⭐ REAL-TIME BROADCAST FOR GROUPS
            room_group = f"group_{group_id}"

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                room_group,
                {
                    "type": "chat_message",
                    "sender": request.user.username,
                    "text": text,
                    "timestamp": timezone.now().strftime("%b. %d, %Y, %-I:%M %p"),
                }
            )

        return redirect("group_chatroom", group_id=group.id)

    return render(request, "group_chatroom.html", {
        "group": group,
        "messages": group.messages.order_by("timestamp"),
    })


@login_required
def create_group(request):
    if request.method == "POST":
        name = request.POST.get("name")
        if name:
            group = Group.objects.create(name=name)
            group.members.add(request.user)
            return redirect("group_chatroom", group.id)
    return render(request, "create_group.html")


@login_required
def delete_user(request, user_id):
    if request.user.id == user_id:
        user = User.objects.get(id=user_id)
        user.delete()
        logout(request)
        return redirect("login")
    return redirect("inbox")


def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = UserCreationForm()
    return render(request, "signup.html", {"form": form})


from django.http import HttpResponse
import os

def debug_settings(request):
    settings_path = os.environ.get('DJANGO_SETTINGS_MODULE', 'Not set')
    return HttpResponse(f"DJANGO_SETTINGS_MODULE: {settings_path}")


from django.conf import settings

def debug_templates(request):
    dirs = settings.TEMPLATES[0]['DIRS']
    return HttpResponse(f"TEMPLATE DIRS: {dirs}")
