"""
Carga preguntas frecuentes iniciales.
Ejecutar: python manage.py seed_faqs
"""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Carga preguntas frecuentes iniciales para Imprint Studio."

    def handle(self, *args, **options):
        from apps.faq.models import FAQ

        if FAQ.objects.exists():
            self.stdout.write("FAQs ya existen, omitiendo.")
            return

        faqs = [
            {
                "question": "¿Qué tipos de archivos aceptan para impresión 3D?",
                "answer": (
                    "Aceptamos archivos en formato STL, OBJ y 3MF. "
                    "Si tienes tu modelo en otro formato, contáctanos y te ayudamos a convertirlo. "
                    "También puedes enviarnos imágenes de referencia y nosotros nos encargamos del modelado."
                ),
                "display_order": 1,
            },
            {
                "question": "¿Cuánto tarda mi pedido?",
                "answer": (
                    "El tiempo de entrega depende de la complejidad y prioridad del pedido:\n"
                    "• Normal: 5 a 7 días hábiles después de confirmar el anticipo.\n"
                    "• Urgente: 2 a 3 días hábiles.\n"
                    "• Express: 1 a 2 días hábiles.\n"
                    "Los tiempos comienzan a contar una vez confirmado el pago del anticipo."
                ),
                "display_order": 2,
            },
            {
                "question": "¿Qué material utilizan?",
                "answer": (
                    "Trabajamos principalmente con PLA, un material biodegradable ideal para la mayoría "
                    "de piezas decorativas y funcionales. Si necesitas otro material (PETG, ABS, TPU), "
                    "consúltanos para verificar disponibilidad y ajustar la cotización."
                ),
                "display_order": 3,
            },
            {
                "question": "¿Cómo funciona el proceso de cotización?",
                "answer": (
                    "1. Creas tu pedido en la plataforma y subes tu archivo 3D o imágenes de referencia.\n"
                    "2. Si subes un archivo STL, recibirás una cotización estimada automática al instante.\n"
                    "3. Revisamos tu pedido y te enviamos la cotización final.\n"
                    "4. Aceptas la cotización y eliges pagar anticipo (50%) o el total.\n"
                    "5. Una vez confirmado el pago, iniciamos la producción."
                ),
                "display_order": 4,
            },
            {
                "question": "¿Qué métodos de pago aceptan?",
                "answer": (
                    "Aceptamos transferencia bancaria y pago en efectivo. "
                    "Al aceptar tu cotización puedes elegir entre pagar el 50% de anticipo o el total "
                    "(con 5% de descuento por pago completo). "
                    "Las instrucciones de pago se muestran en la plataforma después de aceptar la cotización."
                ),
                "display_order": 5,
            },
            {
                "question": "¿Hacen envíos?",
                "answer": (
                    "Sí, hacemos envíos a todo México. El costo de envío se incluye en la cotización. "
                    "También puedes recoger tu pedido directamente en nuestro taller en Tuxtla Gutiérrez, Chiapas, "
                    "sin costo adicional."
                ),
                "display_order": 6,
            },
            {
                "question": "¿Ofrecen garantía en sus impresiones?",
                "answer": (
                    "Sí. Si tu pieza presenta defectos de fabricación (capas despegadas, "
                    "deformaciones o faltantes), la reimprimimos sin costo adicional. "
                    "La garantía no cubre daños por mal uso o modificaciones posteriores. "
                    "Reporta cualquier problema dentro de las primeras 48 horas después de recibir tu pedido."
                ),
                "display_order": 7,
            },
            {
                "question": "¿Puedo cancelar mi pedido?",
                "answer": (
                    "Puedes cancelar tu pedido antes de que entre a producción sin costo. "
                    "Si ya se inició la impresión, no es posible cancelar. "
                    "En caso de cancelación con anticipo pagado, se procesará el reembolso correspondiente."
                ),
                "display_order": 8,
            },
            {
                "question": "¿Pueden imprimir modelos que encuentro en internet?",
                "answer": (
                    "Sí, siempre y cuando el modelo sea de uso libre o tengas la licencia correspondiente. "
                    "Si el modelo es de un sitio de pago, la licencia corre por cuenta del cliente. "
                    "Puedes enviarnos el enlace al modelo y nosotros lo descargamos y preparamos para impresión."
                ),
                "display_order": 9,
            },
            {
                "question": "¿Qué tamaño máximo pueden imprimir?",
                "answer": (
                    "El tamaño máximo depende de la impresora asignada. Nuestras impresoras más grandes "
                    "permiten piezas de hasta 300 × 300 × 300 mm. Para piezas más grandes, "
                    "podemos dividir el modelo en partes y ensamblarlas después de la impresión."
                ),
                "display_order": 10,
            },
        ]

        for faq_data in faqs:
            FAQ.objects.create(**faq_data)

        self.stdout.write(self.style.SUCCESS(f"FAQs: {len(faqs)} preguntas creadas."))
