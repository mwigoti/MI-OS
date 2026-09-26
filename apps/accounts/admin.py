from django.contrib import admin
from .models import UserPreference

@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ("user", "timezone", "email_notifications", "created_at", "updated_at")
    search_fields = ("user__username", "user__email", "timezone")
    list_filter = ("timezone", "email_notifications")
