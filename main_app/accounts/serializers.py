from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers

from .models import Traveler, User


class _EmailValidationMixin:
    def validate_email(self, value):
        return value.strip().lower()


class UserSerializer(_EmailValidationMixin, serializers.ModelSerializer):
    name = serializers.CharField(source="username")

    class Meta:
        model = User
        fields = ["id", "email", "name"]
        read_only_fields = ["id"]


class RegisterSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=150, write_only=True)
    password = serializers.CharField(
        min_length=8,
        trim_whitespace=False,
        style={"input_type": "password"},
        write_only=True,
    )

    def create(self, validated_data):
        name = validated_data.pop("name")
        return User.objects.create_user(username=name, **validated_data)

    def validate_email(self, value):
        value = value.strip().lower()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Этот email уже зарегистрирован")
        return value

    def validate(self, attrs):
        user = User(email=attrs["email"], username=attrs["name"])
        try:
            validate_password(attrs["password"], user=user)
        except DjangoValidationError as exc:
            # ошибки пароля должны прийти в fields.password, а не в non_field_errors
            raise serializers.ValidationError({"password": list(exc.messages)}) from exc
        return attrs

    class Meta:
        model = User
        fields = ["name", "email", "password"]


class LoginSerializer(_EmailValidationMixin, serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True, trim_whitespace=False, style={"input_type": "password"}
    )


class PasswordResetRequestSerializer(_EmailValidationMixin, serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(_EmailValidationMixin, serializers.Serializer):
    token = serializers.CharField(max_length=256, trim_whitespace=True)
    password = serializers.CharField(
        min_length=8,
        trim_whitespace=False,
        style={"input_type": "password"},
        write_only=True,
    )

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate(self, attrs):
        uidb64, sep, token = attrs["token"].partition(":")
        try:
            user = User.objects.get(pk=urlsafe_base64_decode(uidb64).decode())
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            user = None

        if not sep or not user or not default_token_generator.check_token(user, token):
            raise serializers.ValidationError({"token": "Ссылка устарела или неверна"})
        attrs["user"] = user
        return attrs


class TravelerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Traveler
        fields = ["id", "first_name", "last_name", "birth_date"]
        read_only_fields = ["id"]
