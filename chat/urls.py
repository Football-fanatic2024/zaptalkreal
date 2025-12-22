from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.inbox, name="inbox"),
    path("chat/<str:username>/", views.chatroom, name="chatroom"),
    path("group/<int:group_id>/", views.group_chatroom, name="group_chatroom"),
    path("create_group/", views.create_group, name="create_group"),
    path("delete_user/<int:user_id>/", views.delete_user, name="delete_user"),
    path("login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("signup/", views.signup, name="signup"),  # ✅ Added signup route
    path("debug/", views.debug_settings),
    path("debug2/", views.debug_templates),
]


