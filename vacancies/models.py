from django.db import models
from django.urls import reverse
from django.utils.text import slugify

LANGUAGES = ("uz", "de", "en", "ru")


class Vacancy(models.Model):
    slug = models.SlugField(
        max_length=140,
        unique=True,
        blank=True,
        help_text="Bo'sh qoldiring — sarlavhadan avtomatik hosil qilinadi.",
    )
    slots = models.PositiveIntegerField("O'rinlar soni", default=1)
    is_published = models.BooleanField("Chop etilgan (saytda ko'rinadi)", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    title_uz = models.CharField("Sarlavha (o'zbekcha)", max_length=200)
    title_de = models.CharField("Titel (Deutsch)", max_length=200, blank=True)
    title_en = models.CharField("Title (English)", max_length=200, blank=True)
    title_ru = models.CharField("Заголовок (русский)", max_length=200, blank=True)

    location_uz = models.CharField(
        "Manzil / yo'nalish (o'zbekcha)", max_length=200, blank=True,
        help_text="Masalan: Germaniya · Haydovchi / Pochta xizmati",
    )
    location_de = models.CharField("Ort / Bereich (Deutsch)", max_length=200, blank=True)
    location_en = models.CharField("Location / field (English)", max_length=200, blank=True)
    location_ru = models.CharField("Место / направление (русский)", max_length=200, blank=True)

    description_uz = models.TextField(
        "To'liq ma'lumot (o'zbekcha)", blank=True,
        help_text="Vakansiya sahifasida to'liq ko'rinadi: talablar, sharoitlar, maosh va h.k.",
    )
    description_de = models.TextField("Vollständige Beschreibung (Deutsch)", blank=True)
    description_en = models.TextField("Full description (English)", blank=True)
    description_ru = models.TextField("Полное описание (русский)", blank=True)

    class Meta:
        verbose_name = "Vakansiya"
        verbose_name_plural = "Vakansiyalar"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title_uz or self.title_en or f"Vakansiya #{self.pk}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title_en or self.title_uz or "vakansiya") or "vakansiya"
            candidate = base
            i = 2
            while Vacancy.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f"{base}-{i}"
                i += 1
            self.slug = candidate
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("vacancy_detail", kwargs={"slug": self.slug})

    def title(self, lang):
        return getattr(self, f"title_{lang}", "") or self.title_uz

    def location(self, lang):
        return getattr(self, f"location_{lang}", "") or self.location_uz

    def description(self, lang):
        return getattr(self, f"description_{lang}", "") or self.description_uz
