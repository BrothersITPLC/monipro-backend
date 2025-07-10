# from django.contrib.auth import authenticate
# from rest_framework import serializers

# from users.models import User
# from utils import ServiceErrorHandler


# class LoginSerializer(serializers.Serializer):
#     email = serializers.EmailField()
#     password = serializers.CharField()

#     class Meta:
#         model = User
#         fields = ["id", "email"]

#     def validate(self, attrs):
#         email = attrs.get("email")
#         password = attrs.get("password")

#         user = authenticate(
#             request=self.context.get("request"), email=email, password=password
#         )
#         print(user)
#         if not user:
#             raise ServiceErrorHandler(
#                 "Email or password doesn't match. Please try again."
#             )

#         if not user.is_verified:
#             raise ServiceErrorHandler("Account not verified.")

#         # Return the user object instead of just the attributes
#         attrs["user"] = user
#         return attrs


from django.contrib.auth import authenticate
from rest_framework import serializers
from users.models import User
from utils import ServiceErrorHandler

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    class Meta:
        model = User
        fields = ["id", "email"]

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        # 1. Check if the user exists
        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            raise ServiceErrorHandler(
                "Email or password doesn't match. Please try again."
            )

        # 2. Check if user is active
        if not user_obj.is_active:
            raise ServiceErrorHandler(
                "Your account is deactivated. Please contact support."
            )

        # 3. Authenticate credentials
        user = authenticate(
            request=self.context.get("request"), email=email, password=password
        )

        if not user:
            raise ServiceErrorHandler(
                "Email or password doesn't match. Please try again."
            )

        # 4. Check if verified
        if not user.is_verified:
            raise ServiceErrorHandler("Account not verified.")

        # 5. Pass user forward
        attrs["user"] = user
        return attrs

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'

    def validate(self, attrs):
        credentials = {
            'email': attrs.get('email'),
            'password': attrs.get('password'),
        }

        user = authenticate(**credentials)

        if user is None:
            raise serializers.ValidationError('No active account found with the given credentials')

        data = super().validate(attrs)
        return data