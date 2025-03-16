from rest_framework_simplejwt.tokens import AccessToken

from users.models import User


def get_user_from_token(token):
    try:
        # Decode the token
        access_token = AccessToken(token)
        # Extract the user ID from the token payload
        user_id = access_token["user_id"]
        # Retrieve the user from the database
        user = User.objects.get(id=user_id)
        return user
    except User.DoesNotExist:
        return None
    except Exception:
        return None
