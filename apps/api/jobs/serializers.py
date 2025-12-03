import uuid
from decimal import Decimal
from rest_framework import serializers
from apps.jobs.models import Job, JobItem
from apps.api.users.serializers import UserSerializer, DriverProfileSerializer
from apps.configurations.models import VehicleType, ItemCategory

class JobItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = JobItem
        fields = ('id', 'category', 'category_name', 'description', 'weight_kg', 'quantity', 'photo_url')

class JobSerializer(serializers.ModelSerializer):
    customer = UserSerializer(read_only=True)
    driver = UserSerializer(read_only=True)
    items = JobItemSerializer(many=True, read_only=True)
    firebase_tracking_path = serializers.SerializerMethodField()
    
    class Meta:
        model = Job
        fields = (
            'id', 'job_number', 'status', 'customer', 'driver',
            'pickup_address', 'pickup_city', 'pickup_state', 'pickup_lat', 'pickup_lng',
            'pickup_contact_name', 'pickup_contact_phone',
            'delivery_address', 'delivery_city', 'delivery_state', 'delivery_lat', 'delivery_lng',
            'delivery_contact_name', 'delivery_contact_phone',
            'items', 'final_price', 'driver_earnings', 'special_instructions',
            'created_at', 'driver_assigned_at', 'pickup_confirmed_at', 'firebase_tracking_path'
        )
        read_only_fields = fields

    def get_firebase_tracking_path(self, obj):
        if obj.status in ['driver_assigned', 'pickup_confirmed', 'in_transit']:
            return f"/jobs/{obj.id}/driver_location"
        return None

class JobCreateItemSerializer(serializers.ModelSerializer):
    category_id = serializers.UUIDField()
    
    class Meta:
        model = JobItem
        fields = ('category_id', 'description', 'weight_kg', 'quantity')

class JobCreateSerializer(serializers.ModelSerializer):
    items = JobCreateItemSerializer(many=True, write_only=True)
    driver_id = serializers.UUIDField(required=False, allow_null=True)
    vehicle_type_id = serializers.UUIDField()

    class Meta:
        model = Job
        fields = (
            'driver_id', 'vehicle_type_id',
            'pickup_address', 'pickup_city', 'pickup_state', 'pickup_lat', 'pickup_lng',
            'pickup_contact_name', 'pickup_contact_phone',
            'delivery_address', 'delivery_city', 'delivery_state', 'delivery_lat', 'delivery_lng',
            'delivery_contact_name', 'delivery_contact_phone',
            'is_scheduled', 'scheduled_pickup_time', 'special_instructions',
            'items'
        )

    def validate_vehicle_type_id(self, value):
        if not VehicleType.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError("Invalid or inactive vehicle type")
        return value

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("At least one item is required")

        for item in value:
            if not ItemCategory.objects.filter(id=item['category_id'], is_active=True).exists():
                raise serializers.ValidationError(f"Invalid item category: {item['category_id']}")

        return value

    def validate(self, attrs):
        if attrs.get('is_scheduled') and not attrs.get('scheduled_pickup_time'):
            raise serializers.ValidationError({"scheduled_pickup_time": "Required for scheduled jobs"})

        if attrs.get('scheduled_pickup_time'):
            from django.utils import timezone
            if attrs['scheduled_pickup_time'] < timezone.now():
                raise serializers.ValidationError({"scheduled_pickup_time": "Cannot schedule pickup in the past"})

        vehicle_type = VehicleType.objects.get(id=attrs['vehicle_type_id'])
        total_weight = sum(
            Decimal(str(item['weight_kg'])) * item.get('quantity', 1)
            for item in attrs['items']
        )

        if total_weight > vehicle_type.max_weight_kg:
            raise serializers.ValidationError({
                "items": f"Total weight ({total_weight}kg) exceeds vehicle capacity ({vehicle_type.max_weight_kg}kg)"
            })

        return attrs

    def create(self, validated_data):
        from django.db import transaction
        from apps.configurations.utils import calculate_job_pricing
        from apps.payments.models import Payment

        items_data = validated_data.pop('items')
        driver_id = validated_data.pop('driver_id', None)
        vehicle_type_id = validated_data.pop('vehicle_type_id')

        pricing = calculate_job_pricing(
            pickup_lat=validated_data['pickup_lat'],
            pickup_lng=validated_data['pickup_lng'],
            delivery_lat=validated_data['delivery_lat'],
            delivery_lng=validated_data['delivery_lng'],
            vehicle_type_id=vehicle_type_id,
            items_data=items_data
        )

        with transaction.atomic():
            job = Job.objects.create(
                vehicle_type_id=vehicle_type_id,
                driver_id=driver_id,
                job_number=f"JOB-{uuid.uuid4().hex[:8].upper()}",
                distance_km=pricing['distance_km'],
                total_weight_kg=pricing['total_weight_kg'],
                highest_category_multiplier=pricing['highest_category_multiplier'],
                base_price=pricing['base_price'],
                final_price=pricing['final_price'],
                platform_fee=pricing['platform_fee'],
                driver_earnings=pricing['driver_earnings'],
                **validated_data
            )

            for item_data in items_data:
                category_id = item_data.pop('category_id')
                JobItem.objects.create(job=job, category_id=category_id, **item_data)

            commitment_amount = pricing['final_price'] * Decimal('0.5')

            Payment.objects.create(
                job=job,
                customer=self.context['request'].user,
                payment_type='commitment_fee',
                amount=commitment_amount,
                payment_reference=f"PAY-{uuid.uuid4().hex[:10].upper()}",
                paystack_reference=f"PSTK-{uuid.uuid4().hex[:10].upper()}",
                status='pending'
            )

        return job

