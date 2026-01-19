import time
import redis
from django.http import JsonResponse


# Rate Limiting Middleware
class RateLimitMiddleware:
    RATE = 100
    WINDOW = 60  # seconds
    def __init__(self, get_response):
        self.get_response = get_response
        self.redis = redis.Redis(host="localhost", port=6379, db=0)


    def __call__(self, request):
        user_key = request.META.get("REMOTE_ADDR")
        now = time.time()

        pipe = self.redis.pipeline()
        pipe.zadd(user_key, {now: now})
        pipe.zremrangebyscore(user_key, 0, now - self.WINDOW)
        pipe.zcard(user_key)
        pipe.expire(user_key, self.WINDOW)
        _, _, count, _ = pipe.execute()

        if count > self.RATE:
            return JsonResponse({"detail": "Rate limit exceeded"}, status=429)

        return self.get_response(request)
    
    def _get_identifier(self, request):
        return f"rl:{request.META.get('REMOTE_ADDR')}"
