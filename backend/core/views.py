from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.authentication import JWTcookieAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from .utils import SpotifyAuth, AppToken
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from .models import AppUser
from .serializers import UserSerializer
from django.shortcuts import redirect


class UserViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    def get_queryset(self):
        return AppUser.objects.filter(spotify_id=self.request.user.id)
    @action(detail=False, methods=['get'], permission_classes=permission_classes, url_path='me')
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response({'profile':serializer.data}, status=200)

class SpotifyLoginView(APIView):
    def get(self, request):
        auth_url= SpotifyAuth.get_auth_url(request)
        return redirect(auth_url)
        
    

class SpotifyCallbackView(APIView):
    def get(self, request):
        #handles csrf protection via state parameter
        code = request.query_params.get("code")
        state= request.query_params.get("state")
        if state != request.session.get('spotify_auth_state'):
            return Response({"error": "State mismatch. Possible CSRF attack."}, status=400)
        if not code:
            return Response({"error": "Missing authorization code"}, status=400)
        try:
            user = SpotifyAuth.authenticate_user(code)
            refresh = RefreshToken.for_user(user)
            return AppToken.refresh_token(refresh)
        
        except Exception as e:
            return Response({"error": str(e)}, status=400)
class RefreshTokenView(APIView):
    def post(self, request):
        refresh_token= request.COOKIES.get("refresh")
        if not refresh_token:
            return Response({"error": "No refresh token provided"}, status=400)
        try:
            token=RefreshToken(refresh_token)
            return AppToken.refresh_token(token)
          
        
        except Exception:
            return Response({"error": "Invalid refresh token"}, status=400)

class DisplayUserView(APIView):
    def get(self, request):
        print("Authenticated user:", request.user)
        print("cookies: ",request.COOKIES)
        user= request.user
        data= {
            "spotify_id": user.spotify_id,
            "favourite_genres": user.favourite_genres,
        }
        return Response(data)
    

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            token = RefreshToken(request.data["refresh"])
            token.blacklist()
     
            return Response({"success": "Logged out successfully"})
        except Exception:
            return Response({"error": "Invalid token"}, status=400)

