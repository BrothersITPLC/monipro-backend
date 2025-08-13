# accounts/views.py
import json
import time
import hmac
import hashlib
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model, login

User = get_user_model()

def verify_telegram_auth(payload: dict, bot_token: str) -> bool:
    payload = payload.copy()
    hash_received = payload.pop("hash", None)
    if not hash_received:
        return False

    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(payload.items()))
    secret_key = hashlib.sha256(bot_token.encode()).digest()
    computed_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    return hmac.compare_digest(computed_hash, hash_received)

@csrf_exempt
def Telegram_Auth(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    try:
        payload = json.loads(request.body.decode())
    except Exception:
        return JsonResponse({"error": "invalid json"}, status=400)

    bot_token = settings.TELEGRAM_BOT_TOKEN
    if not bot_token:
        return JsonResponse({"error": "server misconfiguration"}, status=500)

    if not verify_telegram_auth(payload, bot_token):
        return JsonResponse({"error": "invalid signature"}, status=403)

    auth_date = int(payload.get("auth_date", 0))
    if time.time() - auth_date > 86400:  # 24 hours max
        return JsonResponse({"error": "auth_date too old"}, status=403)

    telegram_id = int(payload["id"])
    first_name = payload.get("first_name", "")
    last_name = payload.get("last_name", "")
    username = payload.get("username")
    photo_url = payload.get("photo_url")

    try:
        user = User.objects.get(telegram_id=telegram_id)
    except User.DoesNotExist:
        # If the current request has an authenticated user, link Telegram to them
        if request.user.is_authenticated:
            user = request.user
        else:
            # Otherwise, create new user
            user = User.objects.create_user(
                username=f"tg_{telegram_id}",
                first_name=first_name[:150],
                last_name=last_name[:150]
            )
        user.telegram_id = telegram_id
        user.telegram_username = username
        user.telegram_photo_url = photo_url
        user.save()

    # Log them in (Django session auth)
    login(request, user)

    return JsonResponse({
        "ok": True,
        "username": user.username,
        "telegram_username": user.telegram_username,
    })
