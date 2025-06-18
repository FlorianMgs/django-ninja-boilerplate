from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from django.utils.html import format_html

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_api_key_active",
        "api_key_display",
    )
    list_filter = (
        "is_staff",
        "is_superuser",
        "is_active",
        "is_api_key_active",
        "date_joined",
    )
    search_fields = ("username", "first_name", "last_name", "email")
    ordering = ("username",)
    readonly_fields = ("api_key", "date_joined", "last_login")

    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "API Access",
            {
                "fields": ("api_key", "api_key_seed", "is_api_key_active"),
            },
        ),
    )

    actions = ["regenerate_api_keys", "activate_api_keys", "deactivate_api_keys"]

    def api_key_display(self, obj):
        if obj.api_key:
            return format_html(
                '<code style="background: #f0f0f0; padding: 2px 4px; border-radius: 3px;">{}</code>',
                obj.api_key[:12] + "...",
            )
        return "-"

    api_key_display.short_description = "API Key"

    def regenerate_api_keys(self, request, queryset):
        count = 0
        for user in queryset:
            user.regenerate_api_key()
            count += 1

        self.message_user(
            request, f"Successfully regenerated API keys for {count} user(s)."
        )

    regenerate_api_keys.short_description = "Regenerate API keys for selected users"

    def activate_api_keys(self, request, queryset):
        count = queryset.update(is_api_key_active=True)
        self.message_user(
            request, f"Successfully activated API keys for {count} user(s)."
        )

    activate_api_keys.short_description = "Activate API keys for selected users"

    def deactivate_api_keys(self, request, queryset):
        count = queryset.update(is_api_key_active=False)
        self.message_user(
            request, f"Successfully deactivated API keys for {count} user(s)."
        )

    deactivate_api_keys.short_description = "Deactivate API keys for selected users"
