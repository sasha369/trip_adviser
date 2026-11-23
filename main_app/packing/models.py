import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class PackingItem(models.Model):
    """Одна вещь в путешествии пользователя"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    trip = models.ForeignKey(
        "trips.Trip",
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("путешествие"),
    )
    name = models.CharField(max_length=50)
    CATEGORY_CHOICE = [
        (_("одежда"), _("одежда")),
        (_("техника"), _("техника")),
        (_("документы"), _("документы")),
        (_("еда"), _("еда")),
        (_("другое"), _("другое")),
    ]
    category = models.CharField(
        max_length=20, choices=CATEGORY_CHOICE, default=_("другое")
    )
    is_important = models.BooleanField(verbose_name=_("важно"), default=False)
    is_packed = models.BooleanField(verbose_name=_("упаковано"), default=False)

    class Meta:
        ordering = ["name", "category"]
        verbose_name = _("Вещь")
        verbose_name_plural = _("Вещи")

    def __str__(self) -> str:
        return f"{self.category} - {self.name}"


class PackingTemplate(models.Model):
    """Шаблон списка вещей"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("пользователь"),
        related_name="templates",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ["name"]
        verbose_name = _("Шаблон списка вещей")
        verbose_name_plural = _("Шаблоны списков вещей")

    def __str__(self) -> str:
        return str(self.name)


class PackingTemplateItem(models.Model):
    """Предмет из шаблона списка вещей"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(
        PackingTemplate,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("Шаблон списка вещей"),
    )
    name = models.CharField(max_length=50)
    CATEGORY_CHOICE = [
        (_("одежда"), _("одежда")),
        (_("техника"), _("техника")),
        (_("документы"), _("документы")),
        (_("еда"), _("еда")),
        (_("другое"), _("другое")),
    ]
    category = models.CharField(
        max_length=20, choices=CATEGORY_CHOICE, default=_("другое")
    )
    is_important = models.BooleanField(verbose_name=_("важно"), default=True)

    class Meta:
        ordering = ["name", "category"]
        verbose_name = _("Вещь из шаблона")
        verbose_name_plural = _("Вещи из шаблона")

    def __str__(self) -> str:
        return f"{self.category} - {self.name}"
