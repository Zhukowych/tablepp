from django.urls import path, include
from .views import UserProfileDetailView, UserLoginView
from django.contrib.auth.views import LogoutView

urlpatterns = [
     path("user/<int:pk>/", UserProfileDetailView.as_view(), name="user_detail"),
     path('login/', UserLoginView.as_view(), name="login_page"),
     path('logout/', LogoutView.as_view(next_page="/login/"), name="logout")
]
