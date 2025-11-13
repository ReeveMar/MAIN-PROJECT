from django.urls import path

from core.views import SpotifyLoginView, SpotifyCallbackView, UserViewSet,LogoutView

urlpatterns = [
    path("login/", SpotifyLoginView.as_view(), name="spotify-login"),
    path("callback/", SpotifyCallbackView.as_view(), name="spotify-callback"),
    path("users/<int:pk>/", UserViewSet.as_view({'get': 'retrieve'}), name="user-detail"),
    path("logout/", LogoutView.as_view(), name="logout"),
  
]
