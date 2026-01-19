
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import exceptions

class JWTcookieAuthentication(JWTAuthentication):
    def authenticate(self, request):
        raw_token = request.COOKIES.get('access')
        if raw_token is None:
            return None
        try:
            validated_token = self.get_validated_token(raw_token)
            print("Validated token")
        except exceptions.AuthenticationFailed as e:
            raise exceptions.AuthenticationFailed('Invalid token') from e
        
        return self.get_user(validated_token), validated_token

      

        