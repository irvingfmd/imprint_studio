-- ============================================================
-- Imprint Studio
-- schema.sql
-- PostgreSQL 16+
-- Versión: 2.0
-- Estado: Aprobado para implementación
-- ============================================================

-- Cambios v2.0 respecto a v1.0:
-- * Se agrega tabla otp_codes (bloqueante de autenticación).
-- * Se agrega columna is_staff a users (requerido por Django AbstractBaseUser).
-- * Se corrige nombre del campo payment_stage → payment_status (ya estaba
--   correcto en v1.0 del SQL; se documenta la decisión explícitamente).

-- ============================================================
-- EXTENSIONS
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================
-- USERS
-- ============================================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    phone VARCHAR(20) NOT NULL UNIQUE,
    email VARCHAR(255) UNIQUE,

    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100),

    role VARCHAR(20) NOT NULL DEFAULT 'CUSTOMER',

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    -- Requerido por Django AbstractBaseUser para acceso al admin.
    is_staff BOOLEAN NOT NULL DEFAULT FALSE,

    last_login TIMESTAMPTZ,

    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_users_role
        CHECK (role IN ('CUSTOMER', 'ADMIN')),

    CONSTRAINT chk_users_phone_not_empty
        CHECK (phone <> '')
);

CREATE INDEX idx_users_phone ON users(phone);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_is_active ON users(is_active);

-- ============================================================
-- OTP CODES
-- ============================================================

-- Códigos de verificación enviados por WhatsApp.
-- No tiene FK a users porque el OTP puede generarse antes del registro.
-- Los registros pueden eliminarse físicamente después de 24 horas.

CREATE TABLE otp_codes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Teléfono destino en formato E.164.
    phone VARCHAR(20) NOT NULL,

    -- Código numérico de 6 dígitos.
    code VARCHAR(6) NOT NULL,

    -- Indica si ya fue utilizado exitosamente.
    is_used BOOLEAN NOT NULL DEFAULT FALSE,

    -- Contador de intentos fallidos. Máximo 5.
    attempts INTEGER NOT NULL DEFAULT 0,

    -- Timestamp de expiración (10 minutos desde creación).
    expires_at TIMESTAMPTZ NOT NULL,

    -- Timestamp en que fue usado exitosamente.
    used_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_otp_codes_phone_not_empty
        CHECK (phone <> ''),

    CONSTRAINT chk_otp_codes_attempts_non_negative
        CHECK (attempts >= 0),

    CONSTRAINT chk_otp_codes_attempts_max
        CHECK (attempts <= 5)
);

-- Índice para la consulta principal de validación de OTP.
CREATE INDEX idx_otp_codes_phone
ON otp_codes(phone);

CREATE INDEX idx_otp_codes_expires_at
ON otp_codes(expires_at);

CREATE INDEX idx_otp_codes_is_used
ON otp_codes(is_used);

-- Índice compuesto para la consulta de OTP activo por teléfono.
CREATE INDEX idx_otp_codes_phone_active
ON otp_codes(phone, is_used, expires_at);

-- ============================================================
-- SHIPPING ADDRESSES
-- ============================================================

CREATE TABLE shipping_addresses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID NOT NULL,

    address_name VARCHAR(100) NOT NULL,

    street VARCHAR(255) NOT NULL,
    external_number VARCHAR(50) NOT NULL,
    internal_number VARCHAR(50),

    neighborhood VARCHAR(255) NOT NULL,
    postal_code VARCHAR(20) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL DEFAULT 'Mexico',

    references TEXT,

    is_default BOOLEAN NOT NULL DEFAULT FALSE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_shipping_addresses_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE RESTRICT,

    CONSTRAINT chk_shipping_addresses_country_not_empty
        CHECK (country <> '')
);

CREATE INDEX idx_shipping_addresses_user_id ON shipping_addresses(user_id);
CREATE INDEX idx_shipping_addresses_postal_code ON shipping_addresses(postal_code);
CREATE INDEX idx_shipping_addresses_city ON shipping_addresses(city);
CREATE INDEX idx_shipping_addresses_state ON shipping_addresses(state);

-- Solo una dirección predeterminada por usuario.
CREATE UNIQUE INDEX uq_shipping_addresses_default_per_user
ON shipping_addresses(user_id)
WHERE is_default = TRUE;

-- ============================================================
-- ORDERS
-- ============================================================

-- Nombre oficial del campo de estado de pago: payment_status.
-- Valores: NO_PAYMENT, DEPOSIT_PENDING, DEPOSIT_PAID,
--          BALANCE_PENDING, FULLY_PAID, REFUNDED.

CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    customer_id UUID NOT NULL,
    shipping_address_id UUID,

    request_type VARCHAR(30) NOT NULL,

    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,

    color VARCHAR(100),
    quantity INTEGER NOT NULL,

    dimensions_notes TEXT,

    priority VARCHAR(20) NOT NULL DEFAULT 'NORMAL',

    status VARCHAR(50) NOT NULL,

    -- Estado financiero del pedido.
    -- Nombre oficial: payment_status (no payment_stage).
    payment_status VARCHAR(50) NOT NULL DEFAULT 'NO_PAYMENT',

    delivery_method VARCHAR(20) NOT NULL DEFAULT 'PICKUP',

    estimated_delivery_date DATE,

    approved_at TIMESTAMPTZ,
    ready_at TIMESTAMPTZ,
    delivered_at TIMESTAMPTZ,

    cancelled_at TIMESTAMPTZ,
    cancellation_reason TEXT,

    ai_analysis JSONB,
    ai_notes TEXT,
    ai_confidence DECIMAL(5,2),
    ai_category VARCHAR(100),

    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_orders_customer
        FOREIGN KEY (customer_id)
        REFERENCES users(id)
        ON DELETE RESTRICT,

    CONSTRAINT fk_orders_shipping_address
        FOREIGN KEY (shipping_address_id)
        REFERENCES shipping_addresses(id)
        ON DELETE SET NULL,

    CONSTRAINT chk_orders_request_type
        CHECK (request_type IN ('REFERENCE', 'PRINTABLE_FILE')),

    CONSTRAINT chk_orders_priority
        CHECK (priority IN ('NORMAL', 'URGENT', 'EXPRESS')),

    CONSTRAINT chk_orders_status
        CHECK (
            status IN (
                'RECEIVED',
                'PENDING_ANALYSIS',
                'QUOTED',
                'APPROVED',
                'PENDING_DEPOSIT',
                'DEPOSIT_PAID',
                'PRINTING',
                'POST_PROCESSING',
                'READY',
                'PENDING_BALANCE',
                'FULLY_PAID',
                'DELIVERED',
                'CANCELLED'
            )
        ),

    CONSTRAINT chk_orders_payment_status
        CHECK (
            payment_status IN (
                'NO_PAYMENT',
                'DEPOSIT_PENDING',
                'DEPOSIT_PAID',
                'BALANCE_PENDING',
                'FULLY_PAID',
                'REFUNDED'
            )
        ),

    CONSTRAINT chk_orders_delivery_method
        CHECK (delivery_method IN ('PICKUP', 'SHIPPING')),

    CONSTRAINT chk_orders_quantity_positive
        CHECK (quantity > 0),

    CONSTRAINT chk_orders_shipping_address_required
        CHECK (
            delivery_method <> 'SHIPPING'
            OR shipping_address_id IS NOT NULL
        ),

    CONSTRAINT chk_orders_ai_confidence_range
        CHECK (
            ai_confidence IS NULL
            OR (
                ai_confidence >= 0
                AND ai_confidence <= 1
            )
        )
);

CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_shipping_address_id ON orders(shipping_address_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_priority ON orders(priority);
CREATE INDEX idx_orders_request_type ON orders(request_type);
CREATE INDEX idx_orders_delivery_method ON orders(delivery_method);
CREATE INDEX idx_orders_created_at ON orders(created_at);
CREATE INDEX idx_orders_updated_at ON orders(updated_at);

CREATE INDEX idx_orders_status_created_at
ON orders(status, created_at);

CREATE INDEX idx_orders_customer_status
ON orders(customer_id, status);

CREATE INDEX idx_orders_priority_status
ON orders(priority, status);

-- ============================================================
-- REQUEST FILES
-- ============================================================

CREATE TABLE request_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    order_id UUID NOT NULL,
    uploaded_by UUID NOT NULL,

    file_type VARCHAR(30) NOT NULL,
    file_url TEXT NOT NULL,

    original_filename VARCHAR(255) NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    file_size_bytes BIGINT NOT NULL,

    uploaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_request_files_order
        FOREIGN KEY (order_id)
        REFERENCES orders(id)
        ON DELETE RESTRICT,

    CONSTRAINT fk_request_files_uploaded_by
        FOREIGN KEY (uploaded_by)
        REFERENCES users(id)
        ON DELETE RESTRICT,

    CONSTRAINT chk_request_files_file_type
        CHECK (
            file_type IN (
                'IMAGE',
                'STL',
                'OBJ',
                'THREE_MF',
                'PAYMENT_PROOF'
            )
        ),

    CONSTRAINT chk_request_files_size_positive
        CHECK (file_size_bytes > 0)
);

CREATE INDEX idx_request_files_order_id ON request_files(order_id);
CREATE INDEX idx_request_files_uploaded_by ON request_files(uploaded_by);
CREATE INDEX idx_request_files_file_type ON request_files(file_type);
CREATE INDEX idx_request_files_uploaded_at ON request_files(uploaded_at);

-- ============================================================
-- QUOTES
-- ============================================================

CREATE TABLE quotes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    order_id UUID NOT NULL,
    created_by UUID NOT NULL,

    weight_grams DECIMAL(10,2) NOT NULL,
    print_time_hours DECIMAL(10,2) NOT NULL,

    material_cost DECIMAL(10,2) NOT NULL,
    energy_cost DECIMAL(10,2) NOT NULL,
    labor_cost DECIMAL(10,2) NOT NULL,
    post_processing_cost DECIMAL(10,2) NOT NULL,
    packaging_cost DECIMAL(10,2) NOT NULL,
    risk_cost DECIMAL(10,2) NOT NULL,
    shipping_cost DECIMAL(10,2) NOT NULL DEFAULT 0,

    subtotal DECIMAL(10,2) NOT NULL,
    profit_amount DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) NOT NULL DEFAULT 0,
    total_price DECIMAL(10,2) NOT NULL,

    quote_status VARCHAR(20) NOT NULL DEFAULT 'PENDING',

    accepted_at TIMESTAMPTZ,
    rejected_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,

    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_quotes_order
        FOREIGN KEY (order_id)
        REFERENCES orders(id)
        ON DELETE RESTRICT,

    CONSTRAINT fk_quotes_created_by
        FOREIGN KEY (created_by)
        REFERENCES users(id)
        ON DELETE RESTRICT,

    CONSTRAINT chk_quotes_status
        CHECK (
            quote_status IN (
                'PENDING',
                'ACCEPTED',
                'REJECTED',
                'EXPIRED'
            )
        ),

    CONSTRAINT chk_quotes_weight_positive
        CHECK (weight_grams > 0),

    CONSTRAINT chk_quotes_print_time_positive
        CHECK (print_time_hours > 0),

    CONSTRAINT chk_quotes_total_non_negative
        CHECK (total_price >= 0),

    CONSTRAINT chk_quotes_shipping_non_negative
        CHECK (shipping_cost >= 0)
);

CREATE INDEX idx_quotes_order_id ON quotes(order_id);
CREATE INDEX idx_quotes_created_by ON quotes(created_by);
CREATE INDEX idx_quotes_status ON quotes(quote_status);
CREATE INDEX idx_quotes_created_at ON quotes(created_at);
CREATE INDEX idx_quotes_expires_at ON quotes(expires_at);

CREATE INDEX idx_quotes_order_status
ON quotes(order_id, quote_status);

-- Solo una cotización pendiente activa por pedido.
CREATE UNIQUE INDEX uq_quotes_one_pending_per_order
ON quotes(order_id)
WHERE quote_status = 'PENDING'
AND is_deleted = FALSE;

-- ============================================================
-- QUOTE SNAPSHOTS
-- ============================================================

CREATE TABLE quote_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    quote_id UUID NOT NULL UNIQUE,

    material_cost_per_kg DECIMAL(10,2) NOT NULL,
    energy_cost_per_hour DECIMAL(10,2) NOT NULL,
    labor_cost_per_hour DECIMAL(10,2) NOT NULL,
    post_processing_cost_per_gram DECIMAL(10,2) NOT NULL,
    packaging_cost DECIMAL(10,2) NOT NULL,

    failure_percentage DECIMAL(5,2) NOT NULL,
    profit_margin_percentage DECIMAL(5,2) NOT NULL,

    urgent_multiplier DECIMAL(5,2) NOT NULL,
    express_multiplier DECIMAL(5,2) NOT NULL,
    full_payment_discount_percentage DECIMAL(5,2) NOT NULL,

    -- Sin updated_at por diseño: los snapshots son inmutables.
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_quote_snapshots_quote
        FOREIGN KEY (quote_id)
        REFERENCES quotes(id)
        ON DELETE RESTRICT,

    CONSTRAINT chk_quote_snapshots_failure_non_negative
        CHECK (failure_percentage >= 0),

    CONSTRAINT chk_quote_snapshots_profit_non_negative
        CHECK (profit_margin_percentage >= 0),

    CONSTRAINT chk_quote_snapshots_urgent_multiplier
        CHECK (urgent_multiplier >= 1),

    CONSTRAINT chk_quote_snapshots_express_multiplier
        CHECK (express_multiplier >= 1)
);

CREATE INDEX idx_quote_snapshots_quote_id
ON quote_snapshots(quote_id);

-- ============================================================
-- PAYMENTS
-- ============================================================

CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    order_id UUID NOT NULL,

    amount DECIMAL(10,2) NOT NULL,

    payment_type VARCHAR(30) NOT NULL,
    payment_method VARCHAR(30) NOT NULL,
    payment_status VARCHAR(30) NOT NULL DEFAULT 'PENDING',

    proof_file_url TEXT,

    manual_confirmation BOOLEAN NOT NULL DEFAULT FALSE,

    confirmed_by UUID,
    confirmed_at TIMESTAMPTZ,

    notes TEXT,

    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_payments_order
        FOREIGN KEY (order_id)
        REFERENCES orders(id)
        ON DELETE RESTRICT,

    CONSTRAINT fk_payments_confirmed_by
        FOREIGN KEY (confirmed_by)
        REFERENCES users(id)
        ON DELETE RESTRICT,

    CONSTRAINT chk_payments_amount_positive
        CHECK (amount > 0),

    CONSTRAINT chk_payments_type
        CHECK (
            payment_type IN (
                'DEPOSIT',
                'BALANCE',
                'FULL_PAYMENT',
                'REFUND'
            )
        ),

    CONSTRAINT chk_payments_method
        CHECK (
            payment_method IN (
                'BANK_TRANSFER',
                'CASH'
            )
        ),

    CONSTRAINT chk_payments_status
        CHECK (
            payment_status IN (
                'PENDING',
                'CONFIRMED',
                'REJECTED'
            )
        ),

    CONSTRAINT chk_payments_confirmation_data
        CHECK (
            payment_status <> 'CONFIRMED'
            OR confirmed_at IS NOT NULL
        )
);

CREATE INDEX idx_payments_order_id ON payments(order_id);
CREATE INDEX idx_payments_type ON payments(payment_type);
CREATE INDEX idx_payments_method ON payments(payment_method);
CREATE INDEX idx_payments_status ON payments(payment_status);
CREATE INDEX idx_payments_created_at ON payments(created_at);
CREATE INDEX idx_payments_confirmed_at ON payments(confirmed_at);

CREATE INDEX idx_payments_order_status
ON payments(order_id, payment_status);

-- ============================================================
-- PRODUCTION HISTORY
-- ============================================================

CREATE TABLE production_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    order_id UUID NOT NULL,

    previous_status VARCHAR(50),
    new_status VARCHAR(50) NOT NULL,

    changed_by UUID NOT NULL,

    notes TEXT,

    changed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_production_history_order
        FOREIGN KEY (order_id)
        REFERENCES orders(id)
        ON DELETE RESTRICT,

    CONSTRAINT fk_production_history_changed_by
        FOREIGN KEY (changed_by)
        REFERENCES users(id)
        ON DELETE RESTRICT,

    CONSTRAINT chk_production_history_new_status
        CHECK (
            new_status IN (
                'RECEIVED',
                'PENDING_ANALYSIS',
                'QUOTED',
                'APPROVED',
                'PENDING_DEPOSIT',
                'DEPOSIT_PAID',
                'PRINTING',
                'POST_PROCESSING',
                'READY',
                'PENDING_BALANCE',
                'FULLY_PAID',
                'DELIVERED',
                'CANCELLED'
            )
        )
);

CREATE INDEX idx_production_history_order_id
ON production_history(order_id);

CREATE INDEX idx_production_history_changed_at
ON production_history(changed_at);

CREATE INDEX idx_production_history_new_status
ON production_history(new_status);

CREATE INDEX idx_production_history_order_changed_at
ON production_history(order_id, changed_at);

-- ============================================================
-- ORDER EVENTS
-- ============================================================

CREATE TABLE order_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    order_id UUID NOT NULL,

    event_type VARCHAR(100) NOT NULL,
    event_description TEXT,

    metadata JSONB,

    created_by UUID,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_order_events_order
        FOREIGN KEY (order_id)
        REFERENCES orders(id)
        ON DELETE RESTRICT,

    CONSTRAINT fk_order_events_created_by
        FOREIGN KEY (created_by)
        REFERENCES users(id)
        ON DELETE SET NULL,

    CONSTRAINT chk_order_events_type
        CHECK (
            event_type IN (
                'ORDER_CREATED',
                'FILE_UPLOADED',
                'QUOTE_CREATED',
                'QUOTE_ACCEPTED',
                'QUOTE_REJECTED',
                'PAYMENT_PROOF_UPLOADED',
                'PAYMENT_CONFIRMED',
                'PAYMENT_REJECTED',
                'DEPOSIT_CONFIRMED',
                'BALANCE_CONFIRMED',
                'FULL_PAYMENT_CONFIRMED',
                'STATUS_CHANGED',
                'PRIORITY_CHANGED',
                'SHIPPING_ADDRESS_UPDATED',
                'SHIPMENT_CREATED',
                'ORDER_DELIVERED',
                'REFUND_REQUESTED',
                'REFUND_PROCESSED',
                'ORDER_CANCELLED'
            )
        )
);

CREATE INDEX idx_order_events_order_id ON order_events(order_id);
CREATE INDEX idx_order_events_event_type ON order_events(event_type);
CREATE INDEX idx_order_events_created_at ON order_events(created_at);

CREATE INDEX idx_order_events_order_created_at
ON order_events(order_id, created_at);

-- ============================================================
-- SHIPMENTS
-- ============================================================

CREATE TABLE shipments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    order_id UUID NOT NULL UNIQUE,

    carrier_name VARCHAR(100),
    tracking_number VARCHAR(100),

    shipping_cost DECIMAL(10,2) NOT NULL DEFAULT 0,

    shipped_at TIMESTAMPTZ,
    delivered_at TIMESTAMPTZ,

    shipping_notes TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_shipments_order
        FOREIGN KEY (order_id)
        REFERENCES orders(id)
        ON DELETE RESTRICT,

    CONSTRAINT chk_shipments_shipping_cost_non_negative
        CHECK (shipping_cost >= 0)
);

CREATE INDEX idx_shipments_order_id ON shipments(order_id);
CREATE INDEX idx_shipments_tracking_number ON shipments(tracking_number);
CREATE INDEX idx_shipments_shipped_at ON shipments(shipped_at);
CREATE INDEX idx_shipments_delivered_at ON shipments(delivered_at);

-- ============================================================
-- BUSINESS CONFIG
-- ============================================================

CREATE TABLE business_config (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    material_cost_per_kg DECIMAL(10,2) NOT NULL,
    energy_cost_per_hour DECIMAL(10,2) NOT NULL,
    labor_cost_per_hour DECIMAL(10,2) NOT NULL,
    post_processing_cost_per_gram DECIMAL(10,2) NOT NULL,
    packaging_cost DECIMAL(10,2) NOT NULL,

    failure_percentage DECIMAL(5,2) NOT NULL,
    profit_margin_percentage DECIMAL(5,2) NOT NULL,

    urgent_multiplier DECIMAL(5,2) NOT NULL,
    express_multiplier DECIMAL(5,2) NOT NULL,

    full_payment_discount_percentage DECIMAL(5,2) NOT NULL,

    deposit_deadline_hours INTEGER NOT NULL,
    balance_deadline_days INTEGER NOT NULL,

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_business_config_material_non_negative
        CHECK (material_cost_per_kg >= 0),

    CONSTRAINT chk_business_config_energy_non_negative
        CHECK (energy_cost_per_hour >= 0),

    CONSTRAINT chk_business_config_labor_non_negative
        CHECK (labor_cost_per_hour >= 0),

    CONSTRAINT chk_business_config_post_processing_non_negative
        CHECK (post_processing_cost_per_gram >= 0),

    CONSTRAINT chk_business_config_packaging_non_negative
        CHECK (packaging_cost >= 0),

    CONSTRAINT chk_business_config_failure_non_negative
        CHECK (failure_percentage >= 0),

    CONSTRAINT chk_business_config_profit_non_negative
        CHECK (profit_margin_percentage >= 0),

    CONSTRAINT chk_business_config_urgent_multiplier
        CHECK (urgent_multiplier >= 1),

    CONSTRAINT chk_business_config_express_multiplier
        CHECK (express_multiplier >= 1),

    CONSTRAINT chk_business_config_discount_non_negative
        CHECK (full_payment_discount_percentage >= 0),

    CONSTRAINT chk_business_config_deposit_deadline_positive
        CHECK (deposit_deadline_hours > 0),

    CONSTRAINT chk_business_config_balance_deadline_positive
        CHECK (balance_deadline_days > 0)
);

-- Solo una configuración activa.
CREATE UNIQUE INDEX uq_business_config_single_active
ON business_config(is_active)
WHERE is_active = TRUE;

-- ============================================================
-- BUSINESS HOURS
-- ============================================================

CREATE TABLE business_hours (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    weekday INTEGER NOT NULL,
    is_open BOOLEAN NOT NULL DEFAULT TRUE,

    opening_time TIME,
    closing_time TIME,

    notes TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_business_hours_weekday
        CHECK (weekday BETWEEN 1 AND 7),

    CONSTRAINT chk_business_hours_open_times
        CHECK (
            (
                is_open = FALSE
                AND opening_time IS NULL
                AND closing_time IS NULL
            )
            OR
            (
                is_open = TRUE
                AND opening_time IS NOT NULL
                AND closing_time IS NOT NULL
                AND opening_time < closing_time
            )
        )
);

CREATE UNIQUE INDEX uq_business_hours_weekday
ON business_hours(weekday);

-- ============================================================
-- HOLIDAYS
-- ============================================================

CREATE TABLE holidays (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    holiday_date DATE NOT NULL UNIQUE,
    holiday_name VARCHAR(255) NOT NULL,

    affects_shipping BOOLEAN NOT NULL DEFAULT TRUE,
    affects_pickup BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_holidays_name_not_empty
        CHECK (holiday_name <> '')
);

CREATE INDEX idx_holidays_holiday_date ON holidays(holiday_date);

-- ============================================================
-- PAYMENT INSTRUCTIONS
-- ============================================================

CREATE TABLE payment_instructions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    bank_name VARCHAR(100) NOT NULL,
    account_holder VARCHAR(255) NOT NULL,

    account_number VARCHAR(50),
    clabe VARCHAR(30),
    card_number VARCHAR(30),

    additional_notes TEXT,

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_payment_instructions_bank_name_not_empty
        CHECK (bank_name <> ''),

    CONSTRAINT chk_payment_instructions_holder_not_empty
        CHECK (account_holder <> '')
);

-- Solo unas instrucciones activas.
CREATE UNIQUE INDEX uq_payment_instructions_single_active
ON payment_instructions(is_active)
WHERE is_active = TRUE;

-- ============================================================
-- UPDATED_AT TRIGGER
-- ============================================================

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_shipping_addresses_updated_at
BEFORE UPDATE ON shipping_addresses
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_orders_updated_at
BEFORE UPDATE ON orders
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_quotes_updated_at
BEFORE UPDATE ON quotes
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_shipments_updated_at
BEFORE UPDATE ON shipments
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_business_config_updated_at
BEFORE UPDATE ON business_config
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_business_hours_updated_at
BEFORE UPDATE ON business_hours
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_payment_instructions_updated_at
BEFORE UPDATE ON payment_instructions
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

-- ============================================================
-- COMMENTS
-- ============================================================

COMMENT ON TABLE users IS 'Clientes y administradores del sistema.';
COMMENT ON TABLE otp_codes IS 'Códigos OTP para autenticación de usuarios.';
COMMENT ON TABLE orders IS 'Solicitudes de impresión 3D.';
COMMENT ON TABLE shipping_addresses IS 'Direcciones de envío de clientes.';
COMMENT ON TABLE request_files IS 'Archivos asociados a pedidos.';
COMMENT ON TABLE quotes IS 'Cotizaciones oficiales.';
COMMENT ON TABLE quote_snapshots IS 'Snapshot financiero usado al crear una cotización.';
COMMENT ON TABLE payments IS 'Movimientos financieros.';
COMMENT ON TABLE production_history IS 'Historial de cambios de estado.';
COMMENT ON TABLE order_events IS 'Eventos auditables de pedidos.';
COMMENT ON TABLE shipments IS 'Información de envíos.';
COMMENT ON TABLE business_config IS 'Configuración financiera y operativa.';
COMMENT ON TABLE business_hours IS 'Horarios de atención.';
COMMENT ON TABLE holidays IS 'Días festivos.';
COMMENT ON TABLE payment_instructions IS 'Instrucciones bancarias visibles al cliente.';

COMMENT ON COLUMN orders.payment_status IS 'Estado financiero del pedido. Nombre oficial: payment_status.';
COMMENT ON COLUMN users.is_staff IS 'Requerido por Django AbstractBaseUser para acceso al panel de administración.';

-- ============================================================
-- END OF FILE
-- ============================================================