import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class UsernameValidator(UnicodeUsernameValidator):
    """Как стандартный, но без «@»: LoginView по нему отличает почту от логина."""

    regex = r"^[\w.+-]+\Z"
    message = _("Username can only consist of letters, number and symbols . + - _")


class User(AbstractUser):
    """Базовый пользователь, почта - уникальна."""

    email = models.EmailField(
        _("email"),
        unique=True,
        error_messages={"unique": _("User with this email already exists.")},
    )

    name = models.CharField(
        _("name"),
        unique=True,
        validators=[UsernameValidator()],
        error_messages={"unique": _("User with this name already exists")},
    )

    class Meta:  # noqa: D106
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self) -> str:
        return str(self.name)


class Traveler(models.Model):
    """Путник - участник путешествия, может быть прикрепоен к билетам."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="travelers",
        verbose_name=_("user"),
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birth_date = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = _("Traveler")
        verbose_name_plural = _("Travelers")

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()
