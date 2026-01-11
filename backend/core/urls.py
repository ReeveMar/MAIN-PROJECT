from django.urls import path

from core.views import SpotifyLoginView, SpotifyCallbackView, UserViewSet,LogoutView,DisplayUserView, RefreshTokenView

urlpatterns = [
    path("login/", SpotifyLoginView.as_view(), name="spotify-login"),
    path("callback/", SpotifyCallbackView.as_view(), name="spotify-callback"),
    path("users/<int:pk>/", UserViewSet.as_view({'get': 'retrieve'}), name="retrieve-user"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("token/refresh/", RefreshTokenView.as_view(), name="token-refresh"),
    path("users/me/", DisplayUserView.as_view(), name="display-user"),
  
]
