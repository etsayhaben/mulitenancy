from rest_framework import serializers
from .models import User, Product, Order, OrderItem
from decimal import Decimal
from rest_framework import serializers

from rest_framework import serializers


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes additional `fields` or `exclude` arguments
    to control which fields are displayed dynamically.
    """

    def __init__(self, *args, **kwargs):
        # Pop custom arguments
        fields = kwargs.pop("fields", None)
        exclude = kwargs.pop("exclude", None)

        super().__init__(*args, **kwargs)

        if fields is not None:
            # Keep only specified fields
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

        if exclude is not None:
            # Remove excluded fields
            for field_name in exclude:
                self.fields.pop(field_name, None)


class ProductSerializer(DynamicFieldsModelSerializer):
    is_expensive = serializers.SerializerMethodField()
    discount_price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "name",
            "description",
            "price",
            "stock",
            "is_expensive",
            "discount_price",
        )

    def validate(self, attrs):
        if attrs.get("price") is not None and attrs["price"] < 20:
            raise serializers.ValidationError("Price must be at least 20.")
        return super().validate(attrs)

    def get_is_expensive(self, obj):
        return obj.price > 200  # Example threshold for expensive products

    def get_discount_price(self, obj):
        if obj.price > 100:
            return obj.price * Decimal(0.9)
        return obj.price

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.price > 700:
            data["price"] = "Contact us for price"
        return data


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = "__all__"

