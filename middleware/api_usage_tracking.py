from datetime import datetime, timedelta
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache

class APIUsageTrackingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            user_id = request.user.id
            now = datetime.now()
            cache_key = f"api_usage_{user_id}"
            last_request_time = cache.get(cache_key)

            if last_request_time:
                time_diff = now - last_request_time
                if time_diff < timedelta(minutes=1):
                    # Example rate limit: 15 requests per minute
                    request_count = cache.get(f"api_usage_count_{user_id}", 0)
                    if request_count >= 15:
                        from django.http import JsonResponse
                        return JsonResponse({"error": "Rate limit exceeded, from middleware.api_usage_tracking"}, status=429)
                    else:
                        cache.set(f"api_usage_count_{user_id}", request_count + 1, timeout=60)
                else:
                    cache.set(f"api_usage_count_{user_id}", 1, timeout=60)

            cache.set(cache_key, now, timeout=60)

    def process_response(self, request, response):
        return response
