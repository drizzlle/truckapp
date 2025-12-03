from django.contrib import admin
from .models import VehicleType, VehicleYearPricing, ItemCategory, PricingConfig, SystemSetting

@admin.register(VehicleType)
class VehicleTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'max_weight_kg', 'pricing_multiplier', 'is_active', 'display_order')
    list_filter = ('is_active',)
    ordering = ('display_order',)

@admin.register(VehicleYearPricing)
class VehicleYearPricingAdmin(admin.ModelAdmin):
    list_display = ('year_from', 'year_to', 'multiplier', 'is_active')
    list_filter = ('is_active',)

@admin.register(ItemCategory)
class ItemCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'pricing_multiplier', 'is_active', 'display_order')
    list_filter = ('is_active',)
    ordering = ('display_order',)

@admin.register(PricingConfig)
class PricingConfigAdmin(admin.ModelAdmin):
    list_display = ('base_rate_per_km', 'weight_rate_per_kg', 'minimum_fare', 'is_active', 'effective_from')
    list_filter = ('is_active',)

@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    list_display = ('key', 'value_type', 'is_public', 'updated_at')
    list_filter = ('value_type', 'is_public')
    search_fields = ('key', 'description')

