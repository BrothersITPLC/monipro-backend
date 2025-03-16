from django.contrib.auth import get_user_model

User = get_user_model()


class AttachJWTTokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = request.COOKIES.get("access_token")

        if token:
            request.META["HTTP_AUTHORIZATION"] = f"Bearer {token}"

        response = self.get_response(request)
        return response
