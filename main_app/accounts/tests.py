import re

from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.core.cache import cache
from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth.password_validation import validate_password
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Traveler, User

# Пароли для тестов: проходят AUTH_PASSWORD_VALIDATORS
# (не слишком короткий, не слишком общий, не только цифры).
STRONG_PASSWORD = "Xk9!vQ2#mL7@zR4$"
NEW_PASSWORD = "Gf7#yQ1!kW5^tZ9@"


def auth_headers(token: str) -> dict:
    return {"HTTP_AUTHORIZATION": f"Bearer {token}"}


class RegisterAPITests(APITestCase):
    """§7: POST /api/auth/register — регистрация сразу выдаёт JWT."""

    def setUp(self):
        cache.clear()

    def test_register_returns_201_with_tokens_and_user(self):
        response = self.client.post(
            reverse("auth-register"),
            {"name": "Аля", "email": "A@Example.com", "password": STRONG_PASSWORD},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        # email нормализуется к нижнему регистру
        self.assertEqual(response.data["user"]["email"], "a@example.com")
        self.assertEqual(response.data["user"]["name"], "Аля")

        user = User.objects.get(email="a@example.com")
        # имя маппится в username модели (§8 User.name ↔ username)
        self.assertEqual(user.username, "Аля")
        # пароль не хранится в открытом виде
        self.assertTrue(user.check_password(STRONG_PASSWORD))
        self.assertNotEqual(user.password, STRONG_PASSWORD)

    def test_register_rejects_duplicate_email(self):
        User.objects.create_user(
            username="Аля", email="alya@example.com", password=STRONG_PASSWORD
        )

        response = self.client.post(
            reverse("auth-register"),
            {"name": "Аля", "email": "ALYA@example.com", "password": STRONG_PASSWORD},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], "validation_error")
        self.assertIn("email", response.data["fields"])

    def test_register_rejects_missing_fields(self):
        response = self.client.post(reverse("auth-register"), {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], "validation_error")
        self.assertIn("name", response.data["fields"])
        self.assertIn("email", response.data["fields"])
        self.assertIn("password", response.data["fields"])

    def test_register_rejects_common_password(self):
        response = self.client.post(
            reverse("auth-register"),
            {"name": "Аля", "email": "alya@example.com", "password": "secret123"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data["fields"])
        self.assertFalse(User.objects.filter(email="alya@example.com").exists())

    def test_register_response_does_not_leak_password(self):
        payload = {"name": "Аля", "email": "alya@example.com", "password": STRONG_PASSWORD}
        response = self.client.post(reverse("auth-register"), payload, format="json")

        body = str(getattr(response, "data", ""))
        self.assertNotIn(STRONG_PASSWORD, body)


class LoginAPITests(APITestCase):
    """§7: POST /api/auth/login — выдача JWT."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="Аля", email="alya@example.com", password=STRONG_PASSWORD
        )

    def setUp(self):
        cache.clear()

    def test_login_returns_tokens_and_user(self):
        response = self.client.post(
            reverse("auth-login"),
            {"email": "alya@example.com", "password": STRONG_PASSWORD},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["user"]["email"], "alya@example.com")
        self.assertEqual(response.data["user"]["name"], "Аля")

    def test_login_ignores_email_case(self):
        response = self.client.post(
            reverse("auth-login"),
            {"email": "ALYA@EXAMPLE.COM", "password": STRONG_PASSWORD},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_wrong_password_raises_401(self):
        response = self.client.post(
            reverse("auth-login"),
            {"email": "alya@example.com", "password": "wrong-password-1"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # §9: единый формат {code, detail, fields}
        self.assertEqual(response.data["code"], "invalid_credentials")
        self.assertIn("detail", response.data)
        self.assertIn("fields", response.data)
        self.assertNotIn("access", response.data)
        self.assertNotIn("refresh", response.data)

    def test_login_unknown_email_raises_401(self):
        response = self.client.post(
            reverse("auth-login"),
            {"email": "ghost@example.com", "password": STRONG_PASSWORD},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ThrottleTests(APITestCase):
    """§9: throttle на auth-эндпоинтах (~5/мин на IP)."""

    def setUp(self):
        cache.clear()

    def test_sixth_login_attempt_is_throttled(self):
        for _ in range(5):
            self.client.post(
                reverse("auth-login"),
                {"email": "ghost@example.com", "password": "wrong-password-1"},
                format="json",
            )

        response = self.client.post(
            reverse("auth-login"),
            {"email": "ghost@example.com", "password": "wrong-password-1"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertEqual(response.data["code"], "throttled")


class RefreshAPITests(APITestCase):
    """§7: POST /api/auth/refresh — обновление access по refresh."""

    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(
            username="Аля", email="alya@example.com", password=STRONG_PASSWORD
        )

    def test_refresh_returns_new_access_token(self):
        refresh = RefreshToken.for_user(self.user)

        response = self.client.post(
            reverse("auth-refresh"), {"refresh": str(refresh)}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        # новый access работает на защищённом эндпоинте
        profile = self.client.get(reverse("profile"), **auth_headers(response.data["access"]))
        self.assertEqual(profile.status_code, status.HTTP_200_OK)

    def test_refresh_with_invalid_token_raises_401(self):
        response = self.client.post(
            reverse("auth-refresh"), {"refresh": "not-a-real-token"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("code", response.data)
        self.assertIn("detail", response.data)


class ProfileAPITests(APITestCase):
    """§7: GET / PATCH /api/profile — имя и email владельца."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="Аля", email="alya@example.com", password=STRONG_PASSWORD
        )

    def setUp(self):
        cache.clear()

    def test_profile_requires_authentication(self):
        response = self.client.get(reverse("profile"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_profile_returns_current_user(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse("profile"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)
        self.assertEqual(response.data["name"], "Аля")

    def test_patch_profile_updates_name(self):
        self.client.force_authenticate(self.user)
        response = self.client.patch(
            reverse("profile"),
            {"name": "Аля Новая"},
            format="json",
            **auth_headers(self.user.id),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Аля Новая")
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "Аля Новая")

    def test_patch_profile_normalizes_email(self):
        self.client.force_authenticate(self.user)
        response = self.client.patch(
            reverse("profile"),
            {"email": "AlyA@Example.com"},
            format="json",
            **auth_headers(self.user.id),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "alya@example.com")

    def test_profile_rejects_put(self):
        self.client.force_authenticate(self.user)
        response = self.client.put(
            reverse("profile"),
            {"name": "Аля", "email": "alya@example.com"},
            format="json",
            **auth_headers(self.user.id),
        )

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class TravelerAPITests(APITestCase):
    """§7: /api/travelers — путники принадлежат владельцу (ADR-006)."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="Аля", email="alya@example.com", password=STRONG_PASSWORD
        )
        cls.other = User.objects.create_user(
            username="Иван", email="ivan@example.com", password=STRONG_PASSWORD
        )
        cls.other_traveler = Traveler.objects.create(
            user=cls.other, first_name="Пётр", last_name="Чужой"
        )

    def setUp(self):
        cache.clear()
        self.client.force_authenticate(self.user)

    def test_create_traveler_belongs_to_current_user(self):
        response = self.client.post(
            reverse("travelers-list"),
            {"first_name": "Иван", "last_name": "Петров"},
            format="json",
            **auth_headers(self.user.id),
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data["first_name"], "Иван"
        )
        traveler = Traveler.objects.get(id=response.data["id"])
        self.assertEqual(traveler.user_id, self.user.id)

    def test_list_returns_empty_array_without_items(self):
        response = self.client.get(reverse("travelers-list"), **auth_headers(self.user.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_list_shows_only_own_travelers(self):
        Traveler.objects.create(user=self.user, first_name="Маша", last_name="Своя")

        response = self.client.get(reverse("travelers-list"), **auth_headers(self.user.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = {item["last_name"] for item in response.data}
        self.assertEqual(names, {"Своя"})

    def test_other_users_traveler_is_not_reachable(self):
        response = self.client.get(
            reverse("travelers-detail", args=[self.other_traveler.id]),
            **auth_headers(self.user.id),
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_other_users_traveler_cannot_be_updated(self):
        response = self.client.patch(
            reverse("travelers-detail", args=[self.other_traveler.id]),
            {"first_name": "Взломан"},
            format="json",
            **auth_headers(self.user.id),
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.other_traveler.refresh_from_db()
        self.assertEqual(self.other_traveler.first_name, "Пётр")

    def test_other_users_traveler_cannot_be_deleted(self):
        response = self.client.delete(
            reverse("travelers-detail", args=[self.other_traveler.id]),
            **auth_headers(self.user.id),
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(
            Traveler.objects.filter(id=self.other_traveler.id).exists()
        )

    def test_delete_own_traveler(self):
        traveler = Traveler.objects.create(
            user=self.user, first_name="Маша", last_name="Своя"
        )

        response = self.client.delete(
            reverse("travelers-detail", args=[traveler.id]),
            **auth_headers(self.user.id),
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Traveler.objects.filter(id=traveler.id).exists())

    def test_travelers_require_authentication(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(
            reverse("travelers-list"),
            {"first_name": "Иван", "last_name": "Петров"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PasswordResetAPITests(APITestCase):
    """§7: POST /api/auth/reset и /api/auth/reset/confirm."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="Аля", email="alya@example.com", password=STRONG_PASSWORD
        )

    def setUp(self):
        mail.outbox = []
        cache.clear()

    def _request_reset_token(self) -> str:
        response = self.client.post(
            reverse("auth-reset-request"), {"email": self.user.email}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)
        match = re.search(r"Код для сброса пароля: (\S+)", mail.outbox[0].body)
        self.assertIsNotNone(match, "в письме должен быть токен сброса")
        return match.group(1)

    def test_reset_request_sends_email_with_token(self):
        token = self._request_reset_token()

        # токен имеет формат uidb64:token
        self.assertIn(":", token)

    def test_reset_request_ignores_email_case(self):
        response = self.client.post(
            reverse("auth-reset-request"), {"email": "ALYA@EXAMPLE.COM"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)

    def test_reset_request_unknown_email_returns_400_by_field(self):
        response = self.client.post(
            reverse("auth-reset-request"), {"email": "ghost@example.com"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], "validation_error")
        self.assertIn("email", response.data["fields"])
        self.assertEqual(len(mail.outbox), 0)

    def test_confirm_resets_password_and_invalidates_token(self):
        token = self._request_reset_token()

        response = self.client.post(
            reverse("auth-reset-confirm"),
            {"token": token, "password": NEW_PASSWORD},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(NEW_PASSWORD))
        self.assertFalse(self.user.check_password(STRONG_PASSWORD))

        # токен одноразовый: после смены пароля старый не работает
        repeat = self.client.post(
            reverse("auth-reset-confirm"),
            {"token": token, "password": STRONG_PASSWORD},
            format="json",
        )
        self.assertEqual(repeat.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("token", repeat.data["fields"])

    def test_confirm_with_invalid_token_returns_400_by_field(self):
        response = self.client.post(
            reverse("auth-reset-confirm"),
            {"token": "impossible:broken", "password": NEW_PASSWORD},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("token", response.data["fields"])
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(STRONG_PASSWORD))

    def test_confirm_rejects_weak_password(self):
        token = self._request_reset_token()

        response = self.client.post(
            reverse("auth-reset-confirm"),
            {"token": token, "password": "12345678"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data["fields"])
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(STRONG_PASSWORD))
