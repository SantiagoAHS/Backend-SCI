from django.urls import path
from .views import LoginView, RegisterView, UserListView, UserUpdateView

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
     path("register/", RegisterView.as_view(), name="register"),
     path("users/", UserListView.as_view(), name="user-list"),
     path("users/me/", UserUpdateView.as_view(), name="user-update"),

]
