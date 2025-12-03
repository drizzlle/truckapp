from django.contrib import admin
from .models import WaitingList


@admin.register(WaitingList)
class WaitingListAdmin(admin.ModelAdmin):
    list_display = ['email', 'user_type', 'subscribed_at', 'notified']
    list_filter = ['user_type', 'notified', 'subscribed_at']
    search_fields = ['email']
    readonly_fields = ['subscribed_at', 'created_at', 'updated_at']
    list_per_page = 50
    actions = ['mark_as_notified', 'export_to_csv']
    
    def mark_as_notified(self, request, queryset):
        updated = queryset.update(notified=True)
        self.message_user(request, f'{updated} entries marked as notified.')
    mark_as_notified.short_description = 'Mark selected as notified'
    
    def export_to_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="waiting_list.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Email', 'User Type', 'Subscribed At', 'Notified'])
        
        for entry in queryset:
            writer.writerow([
                entry.email,
                entry.user_type,
                entry.subscribed_at.strftime('%Y-%m-%d %H:%M:%S'),
                'Yes' if entry.notified else 'No'
            ])
        
        return response
    export_to_csv.short_description = 'Export selected to CSV'
