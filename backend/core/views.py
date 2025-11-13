from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .utils import SpotifyAuth
from rest_framework.viewsets import ModelViewSet
from .models import AppUser
from .serializers import UserSerializer
class UserViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    def get_queryset(self):
        return AppUser.objects.filter(spotify_id=self.request.user.id)
    
    

class SpotifyLoginView(APIView):
    def get(self, request):
        return Response({"auth_url": SpotifyAuth.get_auth_url(request)})

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
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            })
        except Exception as e:
            return Response({"error": str(e)}, status=400)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            token = RefreshToken(request.data["refresh"])
            token.blacklist()
            return Response({"success": "Logged out successfully"})
        except Exception:
            return Response({"error": "Invalid token"}, status=400)

