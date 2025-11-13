import requests
from datetime import datetime, timedelta
from django.conf import settings
from .models import AppUser 
import secrets

class SpotifyAuth:
    AUTH_URL = "https://accounts.spotify.com/authorize"
    TOKEN_URL = "https://accounts.spotify.com/api/token"
    PROFILE_URL = "https://api.spotify.com/v1/me"
    SCOPES = "user-read-private%20user-read-email%20playlist-read-private%20playlist-read-collaborative%20playlist-modify-public%20playlist-modify-private"
    
    #generate the url to redirect user to spotify's auth page
    @classmethod
    def get_auth_url(cls,request):
        state=secrets.token_urlsafe(16)
        request.session['spotify_auth_state']=state
        
        return (
            f"{cls.AUTH_URL}?response_type=code"
            f"&client_id={settings.SPOTIFY_CLIENT_ID}"
            f"&redirect_uri={settings.SPOTIFY_REDIRECT_URI}"
            f"&scope={cls.SCOPES}"
            f"&state={state}"
            )
    #exchange the authorization code for access and refresh tokens, using csrf protection via state
    @classmethod
    def exchange_code_for_tokens(cls, code):
        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
            "client_id": settings.SPOTIFY_CLIENT_ID,
            "client_secret": settings.SPOTIFY_CLIENT_SECRET,
        }
        response = requests.post(cls.TOKEN_URL, data=payload)
        if response.status_code != 200:
            raise Exception("Failed to obtain tokens from Spotify")
        
        return response.json()
    #obtains the users spotify profile
    @classmethod
    def fetch_user_profile(cls, access_token):
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(cls.PROFILE_URL, headers=headers)
        if response.status_code != 200:
            raise Exception("Failed to fetch Spotify profile")
        return response.json()
    #authenticate user using the authorization code, create or login user in our system
    @classmethod
    def authenticate_user(cls, code):
        tokens = cls.exchange_code_for_tokens(code)
        profile = cls.fetch_user_profile(tokens["access_token"])
        expiry = datetime.now() + timedelta(seconds=tokens["expires_in"])
        user = AppUser.objects.create_or_login_user(
            spotify_id=profile["id"],
            favourite_genres=[],
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_expiry=expiry
        )
        return user
    #refresh the access token using the refresh token
    @classmethod
    def refresh_access_token(cls, refresh_token):
        state=secrets.token_urlsafe(20)
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": settings.SPOTIFY_CLIENT_ID,
            "client_secret": settings.SPOTIFY_CLIENT_SECRET,
            "state": state,
        }
        response = requests.post(cls.TOKEN_URL, data=payload)
        if response.status_code != 200:
            raise Exception("Failed to refresh access token")
  
        return response.json()
    @classmethod
    def get_valid_access_token(cls, user):
        if user.token_expiry>=datetime.now()-timedelta(minutes=5):
            tokens = cls.refresh_access_token(user.refresh_token)
            user.access_token = tokens["access_token"]
            user.token_expiry = datetime.now() + timedelta(seconds=tokens["expires_in"])
            user.save()
        return user.access_token

