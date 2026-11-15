from django.db import models


class TeamMember(models.Model):
    name = models.CharField("Ism familiya", max_length=150)
    subtitle = models.CharField(
        "Qo'shimcha qator (ixtiyoriy)",
        max_length=200,
        blank=True,
        help_text="Masalan: Ai visual Creator, Speaker — ism ostida kichik qatorda chiqadi.",
    )
    role = models.CharField(
        "Katta sarlavha (lavozim)",
        max_length=200,
        help_text="Masalan: CEO, Co-Founder, Graphic Design — kartochkada yirik va qalin shriftda chiqadi.",
    )
    photo = models.ImageField("Surat", upload_to="team/")
    linkedin_url = models.URLField(
        "LinkedIn havolasi",
        blank=True,
        help_text="Bo'sh qoldirilsa, kartochka bosilganda hech qayerga o'tmaydi.",
    )
    order = models.PositiveIntegerField("Tartib raqami", default=0)
    is_published = models.BooleanField("Saytda ko'rinadi", default=True)

    class Meta:
        verbose_name = "Jamoa a'zosi"
        verbose_name_plural = "Jamoa a'zolari"
        ordering = ["order", "id"]

    def __str__(self):
        return self.name
