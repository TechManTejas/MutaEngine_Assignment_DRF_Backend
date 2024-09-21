import logging

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        logger.info(f"Request URL: {request.get_full_path()}")
        logger.info(f"Request Method: {request.method}")
        response = self.get_response(request)
        logger.info(f"Response Status Code: {response.status_code}")
        return response
