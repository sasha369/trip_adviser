from rest_framework import serializers

from .models import PackingItem, PackingTemplate, PackingTemplateItem


class PackingItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackingItem
        fields = ["id", "trip", "name", "category", "is_important", "is_packed"]
        read_only_fields = ["id"]


class PackingTemplateSerializer(serializers.ModelSerializer):
    items = PackingTemplateItem(many=True)

    class Meta:
        model = PackingTemplate
        fields = ["id", "user", "name", "items"]
        read_only_fields = ["id", "user"]


class PackingTemplateItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackingTemplateItem
        fields = ["id", "name", "category", "is_important"]
        read_only_fields = ["id"]
