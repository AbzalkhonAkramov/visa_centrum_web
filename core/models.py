from django.db import models


class ContactMessage(models.Model):
    STATUS_NEW = "new"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_DONE = "done"
    STATUS_CHOICES = [
        (STATUS_NEW, "Yangi"),
        (STATUS_IN_PROGRESS, "Ko'rib chiqilmoqda"),
        (STATUS_DONE, "Yakunlandi"),
    ]

    full_name = models.CharField("F.I.Sh.", max_length=150)
    email = models.EmailField("Email")
    phone = models.CharField("Telefon", max_length=40)
    message = models.TextField("Xabar")
    status = models.CharField(
        "Holat", max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW,
        help_text="Faqat administrator uchun ichki belgi — saytda hech qachon ko'rinmaydi.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Murojaat"
        verbose_name_plural = "Murojaatlar"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} ({self.created_at:%Y-%m-%d %H:%M})"
