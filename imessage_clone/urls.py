from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views

from chat.views import (
    inbox,
    chatroom,
    group_chatroom,
    create_group,
    delete_user,
    signup,
    debug_templates
)

urlpatterns = [
    path("admin/", admin.site.urls),

    # Inbox
    path("", inbox, name="inbox"),

    # 1-on-1 chat
    path("chat/<str:username>/", chatroom, name="chatroom"),

    # Group chat
    path("group/<int:group_id>/", group_chatroom, name="group_chatroom"),

    # Create group
    path("create_group/", create_group, name="create_group"),

    # Delete user
    path("delete_user/<int:user_id>/", delete_user, name="delete_user"),

    # Auth
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("signup/", signup, name="signup"),

    # Debug template directories
    path("debug_templates/", debug_templates),
]
