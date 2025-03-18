from datetime import datetime, timedelta

import jwt
from django.conf import settings


def generate_access_token(user):
    jwt_settings = getattr(settings, "JWT_AUTH", {})
    lifetime = jwt_settings.get("ACCESS_TOKEN_LIFETIME", 300)
    payload = {
        "user_id": user.id,
        "exp": datetime.utcnow() + timedelta(seconds=lifetime),
        "iat": datetime.utcnow(),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return token


def generate_refresh_token(user):
    jwt_settings = getattr(settings, "JWT_AUTH", {})
    lifetime = jwt_settings.get("REFRESH_TOKEN_LIFETIME", 604800)
    payload = {
        "user_id": user.id,
        "exp": datetime.utcnow() + timedelta(seconds=lifetime),
        "iat": datetime.utcnow(),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return token
