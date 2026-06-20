"""
Servicio para generar PDFs de cotizaciones.
"""

from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from apps.quotes.models import Quote


class QuotePDFService:
    """
    Genera un PDF con el desglose de una cotización.
    """

    # Paleta de colores
    COLOR_PRIMARY = colors.HexColor("#1E3A5F")
    COLOR_ACCENT = colors.HexColor("#2563EB")
    COLOR_LIGHT = colors.HexColor("#EFF6FF")
    COLOR_BORDER = colors.HexColor("#BFDBFE")
    COLOR_TEXT = colors.HexColor("#1F2937")
    COLOR_MUTED = colors.HexColor("#6B7280")

    @classmethod
    def generate(cls, quote: Quote) -> bytes:
        buffer = BytesIO()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=2 * cm,
            rightMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )

        styles = getSampleStyleSheet()
        elements = []

        # --- Encabezado ---
        elements += cls._build_header(styles, quote)
        elements.append(Spacer(1, 0.5 * cm))

        # --- Info del pedido ---
        elements += cls._build_order_info(styles, quote)
        elements.append(Spacer(1, 0.5 * cm))

        # --- Desglose de costos ---
        elements += cls._build_cost_breakdown(styles, quote)
        elements.append(Spacer(1, 0.5 * cm))

        # --- Opciones de pago ---
        elements += cls._build_payment_options(styles, quote)
        elements.append(Spacer(1, 0.8 * cm))

        # --- Pie de página ---
        elements += cls._build_footer(styles)

        doc.build(elements)
        return buffer.getvalue()

    @classmethod
    def _build_header(cls, styles, quote: Quote) -> list:
        title_style = ParagraphStyle(
            "Title",
            parent=styles["Normal"],
            fontSize=22,
            textColor=cls.COLOR_PRIMARY,
            fontName="Helvetica-Bold",
            spaceAfter=2,
        )
        subtitle_style = ParagraphStyle(
            "Subtitle",
            parent=styles["Normal"],
            fontSize=10,
            textColor=cls.COLOR_MUTED,
        )
        quote_num_style = ParagraphStyle(
            "QuoteNum",
            parent=styles["Normal"],
            fontSize=10,
            textColor=cls.COLOR_MUTED,
            alignment=2,  # derecha
        )

        date_str = quote.created_at.strftime("%d/%m/%Y")
        quote_short = str(quote.id)[:8].upper()

        header_data = [
            [
                [
                    Paragraph("Imprint Studio", title_style),
                    Paragraph("Impresión 3D Personalizada · Tuxtla Gutiérrez, Chiapas", subtitle_style),
                ],
                [
                    Paragraph(f"COTIZACIÓN #{quote_short}", quote_num_style),
                    Paragraph(f"Fecha: {date_str}", quote_num_style),
                    Paragraph(f"Estado: {quote.quote_status}", quote_num_style),
                ],
            ]
        ]

        header_table = Table(header_data, colWidths=["60%", "40%"])
        header_table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LINEBELOW", (0, 0), (-1, 0), 1.5, cls.COLOR_ACCENT),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ]
            )
        )

        return [header_table]

    @classmethod
    def _build_order_info(cls, styles, quote: Quote) -> list:
        section_style = ParagraphStyle(
            "Section",
            parent=styles["Normal"],
            fontSize=11,
            fontName="Helvetica-Bold",
            textColor=cls.COLOR_PRIMARY,
            spaceBefore=6,
            spaceAfter=4,
        )
        label_style = ParagraphStyle(
            "Label",
            parent=styles["Normal"],
            fontSize=9,
            textColor=cls.COLOR_MUTED,
        )
        value_style = ParagraphStyle(
            "Value",
            parent=styles["Normal"],
            fontSize=9,
            textColor=cls.COLOR_TEXT,
        )

        order = quote.order
        customer = order.customer

        info_data = [
            [Paragraph("Pedido", label_style), Paragraph(order.title, value_style)],
            [
                Paragraph("Cliente", label_style),
                Paragraph(f"{customer.first_name} {customer.last_name}".strip(), value_style),
            ],
            [Paragraph("Tipo", label_style), Paragraph(order.request_type, value_style)],
            [Paragraph("Prioridad", label_style), Paragraph(order.priority, value_style)],
            [Paragraph("Entrega", label_style), Paragraph(order.delivery_method, value_style)],
            [Paragraph("Peso (g)", label_style), Paragraph(f"{quote.weight_grams:,.2f}", value_style)],
            [Paragraph("Tiempo impresión (h)", label_style), Paragraph(f"{quote.print_time_hours:,.2f}", value_style)],
        ]

        info_table = Table(info_data, colWidths=["35%", "65%"])
        info_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (0, -1), cls.COLOR_LIGHT),
                    ("GRID", (0, 0), (-1, -1), 0.5, cls.COLOR_BORDER),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )

        return [Paragraph("Información del Pedido", section_style), info_table]

    @classmethod
    def _build_cost_breakdown(cls, styles, quote: Quote) -> list:
        section_style = ParagraphStyle(
            "Section",
            parent=styles["Normal"],
            fontSize=11,
            fontName="Helvetica-Bold",
            textColor=cls.COLOR_PRIMARY,
            spaceBefore=6,
            spaceAfter=4,
        )

        def row(label: str, value) -> list:
            return [label, f"${value:,.2f} MXN"]

        data = [
            ["Concepto", "Monto"],
            row("Material", quote.material_cost),
            row("Energía", quote.energy_cost),
            row("Mano de obra", quote.labor_cost),
            row("Postprocesado", quote.post_processing_cost),
            row("Empaque", quote.packaging_cost),
            row("Riesgo / fallos", quote.risk_cost),
            row("Envío", quote.shipping_cost),
            row("Subtotal", quote.subtotal),
            row("Ganancia", quote.profit_amount),
        ]

        if quote.discount_amount > 0:
            data.append(["Descuento (pago total)", f"-${quote.discount_amount:,.2f} MXN"])

        if quote.tax_amount > 0:
            data.append(["IVA", f"${quote.tax_amount:,.2f} MXN"])

        # Fila de total
        data.append(["TOTAL", f"${quote.total_price:,.2f} MXN"])

        col_widths = ["70%", "30%"]
        table = Table(data, colWidths=col_widths)

        n = len(data)
        table.setStyle(
            TableStyle(
                [
                    # Encabezado
                    ("BACKGROUND", (0, 0), (-1, 0), cls.COLOR_PRIMARY),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 10),
                    # Filas alternas
                    *[("BACKGROUND", (0, i), (-1, i), cls.COLOR_LIGHT) for i in range(2, n - 1, 2)],
                    # Grid
                    ("GRID", (0, 0), (-1, -1), 0.5, cls.COLOR_BORDER),
                    ("FONTSIZE", (0, 1), (-1, -1), 9),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                    ("RIGHTPADDING", (1, 0), (1, -1), 8),
                    # Fila total
                    ("BACKGROUND", (0, n - 1), (-1, n - 1), cls.COLOR_ACCENT),
                    ("TEXTCOLOR", (0, n - 1), (-1, n - 1), colors.white),
                    ("FONTNAME", (0, n - 1), (-1, n - 1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, n - 1), (-1, n - 1), 11),
                ]
            )
        )

        return [Paragraph("Desglose de Costos", section_style), table]

    @classmethod
    def _build_payment_options(cls, styles, quote: Quote) -> list:
        section_style = ParagraphStyle(
            "Section",
            parent=styles["Normal"],
            fontSize=11,
            fontName="Helvetica-Bold",
            textColor=cls.COLOR_PRIMARY,
            spaceBefore=6,
            spaceAfter=4,
        )
        note_style = ParagraphStyle(
            "Note",
            parent=styles["Normal"],
            fontSize=8,
            textColor=cls.COLOR_MUTED,
            spaceAfter=2,
        )

        from decimal import ROUND_HALF_UP, Decimal

        total = quote.total_price
        deposit = (total / 2).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # Usar el porcentaje del snapshot para que coincida con lo que vería el cliente.
        try:
            discount_pct = quote.snapshot.full_payment_discount_percentage / Decimal("100")
        except Exception:
            discount_pct = Decimal("0.05")
        full_with_discount = (total * (1 - discount_pct)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        data = [
            ["Opción", "Anticipo", "Saldo al entregar", "Total"],
            [
                "50% Anticipo + 50% Entrega",
                f"${deposit:,.2f}",
                f"${deposit:,.2f}",
                f"${total:,.2f}",
            ],
            [
                "100% Anticipado (5% descuento)",
                f"${full_with_discount:,.2f}",
                "—",
                f"${full_with_discount:,.2f}",
            ],
        ]

        table = Table(data, colWidths=["40%", "20%", "20%", "20%"])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), cls.COLOR_PRIMARY),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("GRID", (0, 0), (-1, -1), 0.5, cls.COLOR_BORDER),
                    ("BACKGROUND", (0, 2), (-1, 2), cls.COLOR_LIGHT),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
                    ("RIGHTPADDING", (1, 0), (-1, -1), 8),
                ]
            )
        )

        return [
            Paragraph("Opciones de Pago", section_style),
            table,
            Spacer(1, 0.3 * cm),
            Paragraph(
                "* El anticipo debe realizarse en un plazo máximo de 72 horas para iniciar producción.", note_style
            ),
            Paragraph("* Métodos de pago: transferencia bancaria o efectivo (solo recolección en taller).", note_style),
        ]

    @classmethod
    def _build_footer(cls, styles) -> list:
        footer_style = ParagraphStyle(
            "Footer",
            parent=styles["Normal"],
            fontSize=8,
            textColor=cls.COLOR_MUTED,
            alignment=1,  # centrado
        )

        return [
            Paragraph("─" * 80, footer_style),
            Paragraph(
                "Imprint Studio · Tuxtla Gutiérrez, Chiapas, México · imprintstudio.com",
                footer_style,
            ),
            Paragraph(
                "Esta cotización tiene una vigencia de 7 días a partir de su emisión.",
                footer_style,
            ),
        ]
