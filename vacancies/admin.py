from django.contrib import admin

from .models import Vacancy


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ("title_uz", "location_uz", "slots", "is_published", "updated_at")
    list_editable = ("slots", "is_published")
    list_filter = ("is_published",)
    search_fields = ("title_uz", "title_de", "title_en", "title_ru")
    readonly_fields = ("slug", "created_at", "updated_at")
    fieldsets = (
        ("Umumiy", {"fields": ("slots", "is_published", "slug", "created_at", "updated_at")}),
        ("O'zbekcha", {"fields": ("title_uz", "location_uz", "description_uz")}),
        ("Deutsch", {"fields": ("title_de", "location_de", "description_de")}),
        ("English", {"fields": ("title_en", "location_en", "description_en")}),
        ("Русский", {"fields": ("title_ru", "location_ru", "description_ru")}),
    )
