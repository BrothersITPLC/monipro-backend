from django.middleware.csrf import get_token
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

@api_view(['GET'])
@permission_classes([AllowAny])
def get_csrf_token(request):
    """Endpoint to retrieve CSRF token for API requests"""
    return JsonResponse({'csrfToken': get_token(request)})