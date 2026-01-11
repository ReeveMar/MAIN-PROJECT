from rest_framework import serializers
from django.contrib.auth import get_user_model
AppUser = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppUser
        fields = ['spotify_id', 'access_token', 'refresh_token', 'token_expiry', 'favourite_genres']
        read_only_fields = ['spotify_id', 'access_token', 'refresh_token', 'token_expiry']
