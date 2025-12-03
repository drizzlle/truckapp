from django.contrib import admin
from .models import Payment, Payout

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_reference', 'job', 'customer', 'amount', 'payment_type', 'status', 'created_at')
    list_filter = ('status', 'payment_type', 'created_at')
    search_fields = ('payment_reference', 'job__job_number', 'customer__username', 'paystack_reference')

@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    list_display = ('payout_reference', 'job', 'driver', 'net_amount', 'payout_type', 'status', 'created_at')
    list_filter = ('status', 'payout_type', 'created_at')
    search_fields = ('payout_reference', 'job__job_number', 'driver__username')

