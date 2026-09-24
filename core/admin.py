from django.contrib import admin

from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "phone", "status", "created_at")
    list_editable = ("status",)
    list_filter = ("status",)
    search_fields = ("full_name", "email", "phone", "message")
    readonly_fields = ("full_name", "email", "phone", "message", "created_at")
    fields = ("full_name", "email", "phone", "message", "status", "created_at")

    def has_add_permission(self, request):
        # Messages only ever come from the site's contact form.
        return False
