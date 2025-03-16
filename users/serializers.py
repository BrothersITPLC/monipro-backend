from tokenize import TokenError

from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import DjangoUnicodeDecodeError, force_bytes, smart_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User
from utils.otp_send_email import EmailHandler


class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    class Meta:
        model = User
        fields = ["id", "email"]

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(
            request=self.context.get("request"), email=email, password=password
        )
        if not user:
            raise serializers.ValidationError(
                {
                    "status": "error",
                    "message": "Email or password doesn't match. Please try again.",
                }
            )

        if not user.is_verified:
            raise serializers.ValidationError(
                {"status": "error", "message": "Account not verified."}
            )
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        fields = ["id", "user", "name"]


class UserChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        max_length=255, style={"input_type": "password"}, write_only=True
    )
    password = serializers.CharField(
        max_length=255, style={"input_type": "password"}, write_only=True
    )
    password2 = serializers.CharField(
        max_length=255, style={"input_type": "password"}, write_only=True
    )

    class Meta:
        fields = ["old_password", "new_password", "password2"]

    def validate(self, attrs):
        old_password = attrs.get("old_password")
        password = attrs.get("password")
        password2 = attrs.get("password2")
        user = self.context.get("user")
        if not check_password(old_password, user.password):
            raise serializers.ValidationError(
                {"status": "error", "message": "Old Password is Incorrect."}
            )

        if password == old_password:
            raise serializers.ValidationError(
                {
                    "status": "error",
                    "message": "New Password must be different from the Old Password.",
                }
            )

        if password != password2:
            raise serializers.ValidationError(
                {
                    "status": "error",
                    "message": "New Password and Confirm Password don't match.",
                }
            )
        return attrs

    def save(self, **kwargs):
        user = self.context.get("user")
        password = self.validated_data["password"]
        user.set_password(password)
        user.save()
        return user


class SendPasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        fields = ["email"]

    def validate(self, attrs):
        email = attrs.get("email")
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            link = (
                "http://localhost:8000/api/user/reset-password/"
                + uid
                + "/"
                + token
                + "/"
            )
            body = "Your password reset link is " + link
            data = {
                "subject": "Password reset",
                "body": body,
                "to_email": user,
            }
            EmailHandler.send_email(data)

            return attrs
        else:
            raise serializers.ValidationError(
                {"status": "error", "message": "Email not found."}
            )


class UserPasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(
        max_length=255, style={"input_type": "password"}, write_only=True
    )
    password2 = serializers.CharField(
        max_length=255, style={"input_type": "password"}, write_only=True
    )

    class Meta:
        fields = ["password", "password2"]

    def validate(self, attrs):
        try:
            password = attrs.get("password")
            password2 = attrs.get("password2")
            uid = self.context.get("uid")
            token = self.context.get("token")
            if password != password2:
                raise serializers.ValidationError(
                    {
                        "status": "error",
                        "message": "Password and Confirm Password don't match.",
                    }
                )
            id = smart_str(urlsafe_base64_decode(uid))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError(
                    {"status": "error", "message": "Invalid token."}
                )
            user.set_password(password)
            user.save()
            return attrs
        except DjangoUnicodeDecodeError:
            PasswordResetTokenGenerator().check_token(user, token)
            raise serializers.ValidationError(
                {"status": "error", "message": "Invalid token."}
            )


class UserLogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs.get("refresh")
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            raise serializers.ValidationError(
                {"status": "error", "message": "Invalid token."}
            )
