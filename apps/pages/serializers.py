from rest_framework import serializers
from .models import WaitingList


class WaitingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaitingList
        fields = ['email', 'user_type']
    
    def validate_email(self, value):
        if WaitingList.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already on the waiting list.")
        return value.lower()
