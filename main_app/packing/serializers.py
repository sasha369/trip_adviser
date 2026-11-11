from rest_framework import serializers

from .models import PackingItem, PackingTemplate, PackingTemplateItem


class PackingItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackingItem
        fields = ["id", "trip", "name", "category", "is_important", "is_packed"]
        read_only_fields = ["id", "trip"]


class PackingTemplateSerializer(serializers.ModelSerializer):
    items = PackingTemplateItem(many=True)

    class Meta:
        model = PackingTemplate
        fields = ["id", "user", "name", "items"]
        read_only_fields = ["id", "user"]

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        template = PackingTemplate.objects.create(**validated_data)
        PackingTemplateItem.objects.bulk_create(
            [PackingTemplateItem(template=template, **item) for item in items_data]
        )
        return template

    def update(self, instance, validated_data):
        items_data = validated_data.pop("items", None)
        instance = super().update(instance, validated_data)
        if items_data is not None:
            instance.items.all().delete()
            PackingTemplateItem.objects.bulk_create(
                [PackingTemplateItem(template=instance, **item) for item in items_data]
            )
        return instance


class PackingTemplateItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackingTemplateItem
        fields = ["id", "name", "category", "is_important"]
        read_only_fields = ["id"]
