from decimal import Decimal
from geopy.distance import geodesic
from django.shortcuts import get_object_or_404

from .models import PricingConfig, VehicleType, ItemCategory


def calculate_job_pricing(pickup_lat, pickup_lng, delivery_lat, delivery_lng,
                          vehicle_type_id, items_data):
    """
    Calculate pricing for a job based on distance, weight, and multipliers.

    Args:
        pickup_lat: Pickup latitude
        pickup_lng: Pickup longitude
        delivery_lat: Delivery latitude
        delivery_lng: Delivery longitude
        vehicle_type_id: UUID of vehicle type
        items_data: List of dicts with 'weight_kg', 'quantity', 'category_id'

    Returns:
        dict with pricing details
    """
    config = PricingConfig.objects.filter(is_active=True).first()
    if not config:
        config = PricingConfig(
            base_rate_per_km=Decimal('50.0'),
            weight_rate_per_kg=Decimal('10.0'),
            minimum_fare=Decimal('500.0'),
            platform_fee_percentage=Decimal('10.0')
        )

    pickup = (float(pickup_lat), float(pickup_lng))
    delivery = (float(delivery_lat), float(delivery_lng))
    distance_km = Decimal(str(geodesic(pickup, delivery).kilometers))

    total_weight_kg = Decimal('0.0')
    highest_category_multiplier = Decimal('1.0')

    for item in items_data:
        weight = Decimal(str(item.get('weight_kg', 0)))
        quantity = int(item.get('quantity', 1))
        total_weight_kg += weight * quantity

        category_id = item.get('category_id')
        if category_id:
            try:
                cat = ItemCategory.objects.get(id=category_id)
                if cat.pricing_multiplier > highest_category_multiplier:
                    highest_category_multiplier = cat.pricing_multiplier
            except ItemCategory.DoesNotExist:
                pass

    vehicle_type = get_object_or_404(VehicleType, id=vehicle_type_id)
    vehicle_multiplier = vehicle_type.pricing_multiplier

    distance_cost = distance_km * config.base_rate_per_km
    weight_cost = total_weight_kg * config.weight_rate_per_kg

    base_subtotal = distance_cost + weight_cost

    total_multiplier = highest_category_multiplier * vehicle_multiplier

    estimated_price = base_subtotal * total_multiplier

    final_price = max(estimated_price, config.minimum_fare)

    platform_fee = final_price * (config.platform_fee_percentage / Decimal('100.0'))
    driver_earnings = final_price - platform_fee

    return {
        'distance_km': distance_km,
        'total_weight_kg': total_weight_kg,
        'base_price': base_subtotal,
        'highest_category_multiplier': highest_category_multiplier,
        'vehicle_multiplier': vehicle_multiplier,
        'final_price': final_price,
        'platform_fee': platform_fee,
        'driver_earnings': driver_earnings,
    }
