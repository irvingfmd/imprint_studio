```sql
-- ============================================================
-- Imprint Studio
-- seed.sql
-- PostgreSQL 16+
-- Versión: 1.0
-- Estado: Aprobado para implementación
-- ============================================================

-- Este archivo contiene datos iniciales para una instalación nueva.
-- Debe ejecutarse después de schema.sql.

-- ============================================================
-- BUSINESS CONFIG
-- ============================================================

INSERT INTO business_config (
    material_cost_per_kg,
    energy_cost_per_hour,
    labor_cost_per_hour,
    post_processing_cost_per_gram,
    packaging_cost,
    failure_percentage,
    profit_margin_percentage,
    urgent_multiplier,
    express_multiplier,
    full_payment_discount_percentage,
    deposit_deadline_hours,
    balance_deadline_days,
    is_active
)
VALUES (
    25.00,
    0.50,
    15.00,
    0.05,
    2.00,
    10.00,
    30.00,
    1.30,
    1.50,
    5.00,
    72,
    7,
    TRUE
);

-- ============================================================
-- BUSINESS HOURS
-- ============================================================

INSERT INTO business_hours (
    weekday,
    is_open,
    opening_time,
    closing_time,
    notes
)
VALUES
    (1, TRUE, '09:00', '18:00', 'Horario normal'),
    (2, TRUE, '09:00', '18:00', 'Horario normal'),
    (3, TRUE, '09:00', '18:00', 'Horario normal'),
    (4, TRUE, '09:00', '18:00', 'Horario normal'),
    (5, TRUE, '09:00', '18:00', 'Horario normal'),
    (6, TRUE, '09:00', '14:00', 'Horario reducido'),
    (7, FALSE, NULL, NULL, 'Cerrado');

-- ============================================================
-- HOLIDAYS
-- ============================================================

INSERT INTO holidays (
    holiday_date,
    holiday_name,
    affects_shipping,
    affects_pickup
)
VALUES
    ('2026-01-01', 'Año Nuevo', TRUE, TRUE),
    ('2026-02-05', 'Día de la Constitución Mexicana', TRUE, TRUE),
    ('2026-03-16', 'Natalicio de Benito Juárez', TRUE, TRUE),
    ('2026-05-01', 'Día del Trabajo', TRUE, TRUE),
    ('2026-09-16', 'Día de la Independencia de México', TRUE, TRUE),
    ('2026-11-16', 'Día de la Revolución Mexicana', TRUE, TRUE),
    ('2026-12-25', 'Navidad', TRUE, TRUE);

-- ============================================================
-- PAYMENT INSTRUCTIONS
-- ============================================================

INSERT INTO payment_instructions (
    bank_name,
    account_holder,
    account_number,
    clabe,
    card_number,
    additional_notes,
    is_active
)
VALUES (
    'BBVA',
    'Imprint Studio',
    NULL,
    NULL,
    NULL,
    'Configurar datos bancarios reales antes de producción. El cliente debe enviar comprobante después de realizar la transferencia.',
    TRUE
);

-- ============================================================
-- OPTIONAL ADMIN PLACEHOLDER
-- ============================================================

-- El usuario administrador debe crearse mediante Django:
--
-- python manage.py createsuperuser
--
-- No se recomienda insertar usuarios manualmente desde SQL porque
-- Django gestiona passwords, permisos y autenticación internamente.

-- ============================================================
-- VALIDATION QUERIES
-- ============================================================

-- Verificar configuración activa:
--
-- SELECT * FROM business_config WHERE is_active = TRUE;
--
-- Verificar horarios:
--
-- SELECT * FROM business_hours ORDER BY weekday;
--
-- Verificar instrucciones de pago:
--
-- SELECT * FROM payment_instructions WHERE is_active = TRUE;

-- ============================================================
-- END OF FILE
-- ============================================================
```
