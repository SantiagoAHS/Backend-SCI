from django.urls import path
from .views import LoginView, RegisterView, UserListView, UserProfileUpdateView, UserDeleteView, UserUpdateView, UserProfileView

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
     path("register/", RegisterView.as_view(), name="register"),
     path("users/", UserListView.as_view(), name="user-list"),
     path("users/<int:pk>/delete/", UserDeleteView.as_view(), name="user-delete"),
      path("users/<int:pk>/update/", UserUpdateView.as_view(), name="user-update-admin"),
     path("users/me/", UserProfileUpdateView.as_view(), name="user-update"),
     path("perfil/", UserProfileView.as_view()),
]
