from rest_framework import serializers
from apps.configurations.models import VehicleType, ItemCategory, PricingConfig

class VehicleTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleType
        fields = ('id', 'name', 'description', 'max_weight_kg', 'pricing_multiplier', 'icon_url')

class ItemCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCategory
        fields = ('id', 'name', 'description', 'pricing_multiplier', 'icon_url')

class PriceCalculationSerializer(serializers.Serializer):
    pickup_lat = serializers.DecimalField(max_digits=10, decimal_places=8)
    pickup_lng = serializers.DecimalField(max_digits=11, decimal_places=8)
    delivery_lat = serializers.DecimalField(max_digits=10, decimal_places=8)
    delivery_lng = serializers.DecimalField(max_digits=11, decimal_places=8)
    vehicle_type_id = serializers.UUIDField()
    items = serializers.ListField(child=serializers.DictField())
