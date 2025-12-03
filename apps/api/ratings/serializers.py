from rest_framework import serializers
from apps.ratings.models import Rating

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ('id', 'job', 'rating', 'review', 'professionalism', 'timeliness', 'vehicle_condition', 'created_at')
        read_only_fields = ('id', 'created_at', 'rater', 'ratee', 'rater_type')

class RatingCreateSerializer(serializers.ModelSerializer):
    job_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Rating
        fields = ('job_id', 'rating', 'review', 'professionalism', 'timeliness', 'vehicle_condition')

