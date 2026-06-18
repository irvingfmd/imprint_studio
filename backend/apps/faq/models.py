"""
Modelos para la app faq.
"""

from django.db import models

from core.models import BaseModel


class FAQ(BaseModel):
    """Pregunta frecuente con respuesta, ordenable y activable."""

    question = models.CharField(max_length=500)
    answer = models.TextField()
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["display_order", "created_at"]
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"

    def __str__(self) -> str:
        return self.question[:80]
