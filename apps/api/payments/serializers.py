from rest_framework import serializers
from apps.payments.models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    job_number = serializers.CharField(source='job.job_number', read_only=True)
    
    class Meta:
        model = Payment
        fields = ('id', 'payment_reference', 'job_number', 'payment_type', 'amount', 'status', 'created_at')

