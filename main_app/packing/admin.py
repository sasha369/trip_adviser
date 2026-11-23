from django.contrib import admin

from .models import PackingItem, PackingTemplate, PackingTemplateItem


@admin.register(PackingItem)
class ItemAdmin(admin.ModelAdmin):
    fields = ["trip", "name", "category", "is_important", "is_packed"]


@admin.register(PackingTemplate)
class TemplateAdmin(admin.ModelAdmin):
    fields = ["user", "name"]


@admin.register(PackingTemplateItem)
class TemplateItemAdmin(admin.ModelAdmin):
    fields = ["template", "name", "category", "is_important"]
