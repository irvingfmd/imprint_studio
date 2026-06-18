"""
Servicios para la app faq.
"""
from .models import FAQ


class FAQService:

    @staticmethod
    def create_faq(data: dict) -> FAQ:
        """Crea una nueva FAQ."""
        return FAQ.objects.create(
            question=data["question"],
            answer=data["answer"],
            display_order=data.get("display_order", 0),
            is_active=data.get("is_active", True),
        )

    @staticmethod
    def update_faq(faq: FAQ, data: dict) -> FAQ:
        """Actualiza una FAQ existente."""
        faq.question = data["question"]
        faq.answer = data["answer"]
        faq.display_order = data.get("display_order", faq.display_order)
        faq.is_active = data.get("is_active", faq.is_active)
        faq.save(update_fields=["question", "answer", "display_order", "is_active", "updated_at"])
        return faq

    @staticmethod
    def delete_faq(faq: FAQ) -> None:
        """Elimina una FAQ (hard delete — no es entidad crítica)."""
        faq.delete()
