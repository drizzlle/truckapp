from rest_framework import generics, views, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from geopy.distance import geodesic
from django.shortcuts import get_object_or_404

from apps.configurations.models import VehicleType, ItemCategory, PricingConfig, VehicleYearPricing
from .serializers import VehicleTypeSerializer, ItemCategorySerializer, PriceCalculationSerializer

class VehicleTypeListView(generics.ListAPIView):
    queryset = VehicleType.objects.filter(is_active=True).order_by('display_order')
    serializer_class = VehicleTypeSerializer
    permission_classes = (AllowAny,)

class ItemCategoryListView(generics.ListAPIView):
    queryset = ItemCategory.objects.filter(is_active=True).order_by('display_order')
    serializer_class = ItemCategorySerializer
    permission_classes = (AllowAny,)

class CalculatePriceView(views.APIView):
    permission_classes = (AllowAny,)
    
    def post(self, request):
        serializer = PriceCalculationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        # Get Pricing Config
        config = PricingConfig.objects.filter(is_active=True).first()
        if not config:
            # Fallback defaults if no config exists
            config = PricingConfig(
                base_rate_per_km=50.0,
                weight_rate_per_kg=10.0,
                minimum_fare=500.0,
                platform_fee_percentage=10.0
            )
            
        # Calculate Distance
        pickup = (data['pickup_lat'], data['pickup_lng'])
        delivery = (data['delivery_lat'], data['delivery_lng'])
        distance_km = geodesic(pickup, delivery).kilometers
        
        # Calculate Weight and Item Multipliers
        total_weight_kg = 0
        highest_category_multiplier = 1.0
        
        items = data.get('items', [])
        for item in items:
            weight = item.get('weight_kg', 0)
            quantity = item.get('quantity', 1)
            total_weight_kg += float(weight) * int(quantity)
            
            category_id = item.get('category_id')
            if category_id:
                try:
                    cat = ItemCategory.objects.get(id=category_id)
                    if cat.pricing_multiplier > highest_category_multiplier:
                        highest_category_multiplier = cat.pricing_multiplier
                except ItemCategory.DoesNotExist:
                    pass
        
        # Get Vehicle Multiplier
        vehicle_type = get_object_or_404(VehicleType, id=data['vehicle_type_id'])
        vehicle_multiplier = vehicle_type.pricing_multiplier
        
        # Basic Price Calculation Formula
        # (Distance * Rate + Weight * Rate) * Multipliers
        
        distance_cost = float(distance_km) * float(config.base_rate_per_km)
        weight_cost = float(total_weight_kg) * float(config.weight_rate_per_kg)
        
        base_subtotal = distance_cost + weight_cost
        
        # Apply Multipliers
        total_multiplier = float(highest_category_multiplier) * float(vehicle_multiplier)
        
        # Vehicle Year Multiplier (Optional - simplified here as we don't have vehicle year in request usually, 
        # unless it's tied to a specific driver, but this is a general estimate)
        # For now, ignore year multiplier or assume standard 1.0 for estimate
        
        estimated_price = base_subtotal * total_multiplier
        
        # Ensure minimum fare
        final_price = max(estimated_price, float(config.minimum_fare))
        
        # Calculate fees
        platform_fee = final_price * (float(config.platform_fee_percentage) / 100.0)
        driver_earnings = final_price - platform_fee
        commitment_fee = final_price * 0.5 # 50%
        
        return Response({
            "distance_km": round(distance_km, 2),
            "total_weight_kg": total_weight_kg,
            "base_price": round(base_subtotal, 2),
            "highest_category_multiplier": float(highest_category_multiplier),
            "vehicle_multiplier": float(vehicle_multiplier),
            "final_price": round(final_price, 2),
            "platform_fee": round(platform_fee, 2),
            "driver_earnings": round(driver_earnings, 2),
            "commitment_fee": round(commitment_fee, 2),
            "breakdown": {
                "distance_cost": round(distance_cost, 2),
                "weight_cost": round(weight_cost, 2)
            }
        })
