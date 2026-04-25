-- ============================================================
--  Smart Access — Full Schema
--  Run this manually in Supabase SQL Editor or psql
--  Order: enums → tables (dependency-aware) → indexes
-- ============================================================

-- ── Extensions ──────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS "pgcrypto";  -- gen_random_uuid()

-- ============================================================
--  ENUM TYPES
-- ============================================================

CREATE TYPE user_role AS ENUM (
    'super_admin', 'admin_hub', 'admin_ops', 'merchant', 'parent'
);

CREATE TYPE account_status AS ENUM (
    'active', 'inactive', 'suspended', 'pending_deletion'
);

CREATE TYPE region_status AS ENUM (
    'active', 'suspended'
);

CREATE TYPE school_type AS ENUM (
    'sd', 'smp', 'sma', 'smk', 'boarding', 'university'
);

CREATE TYPE school_status AS ENUM (
    'active', 'pending_approval', 'suspended'
);

CREATE TYPE business_type AS ENUM (
    'kantin', 'laundry', 'minimarket', 'fotokopi', 'other'
);

CREATE TYPE merchant_status AS ENUM (
    'active', 'suspended'
);

CREATE TYPE client_status AS ENUM (
    'active', 'inactive', 'suspended', 'locked', 'pending_deletion', 'deleted'
);

CREATE TYPE device_type AS ENUM (
    'fingerprint_reader', 'face_camera', 'combo_device'
);

CREATE TYPE device_status AS ENUM (
    'active', 'offline', 'maintenance', 'retired', 'registered', 'blocked'
);

CREATE TYPE wallet_status AS ENUM (
    'active', 'frozen', 'closed'
);

CREATE TYPE ledger_type AS ENUM (
    'topup', 'debit', 'refund', 'adjustment'
);

CREATE TYPE transaction_type AS ENUM (
    'topup', 'purchase', 'refund', 'withdrawal'
);

CREATE TYPE transaction_status AS ENUM (
    'pending', 'success', 'failed', 'refunded', 'expired'
);

CREATE TYPE payment_method AS ENUM (
    'qris', 'bank_transfer', 'va'
);

CREATE TYPE biometric_method AS ENUM (
    'fingerprint_face', 'fallback_pin'
);

CREATE TYPE credential_status AS ENUM (
    'active', 'inactive', 'revoked'
);

CREATE TYPE product_category AS ENUM (
    'makanan', 'minuman', 'snack', 'jasa', 'lainnya'
);

CREATE TYPE ticket_category AS ENUM (
    'transaction', 'biometric', 'account', 'other'
);

CREATE TYPE ticket_priority AS ENUM (
    'low', 'medium', 'high', 'critical'
);

CREATE TYPE ticket_status AS ENUM (
    'open', 'in_progress', 'resolved', 'closed'
);

CREATE TYPE approval_request_type AS ENUM (
    'create_admin_ops', 'delete_admin_ops', 'refund'
);

CREATE TYPE approval_status AS ENUM (
    'pending', 'approved', 'rejected'
);

CREATE TYPE audit_event_type AS ENUM (
    'auth', 'user_mgmt', 'biometric', 'transaction', 'financial', 'system', 'support'
);

CREATE TYPE audit_result AS ENUM (
    'success', 'failure'
);

CREATE TYPE notification_type AS ENUM (
    'transaction', 'topup', 'limit_alert', 'account_lock', 'approval', 'sla_breach', 'system'
);

-- ============================================================
--  TABLES
-- ============================================================

-- ── 1. users ─────────────────────────────────────────────────
CREATE TABLE users (
    id              VARCHAR(36)     PRIMARY KEY DEFAULT gen_random_uuid()::text,
    email           VARCHAR(255)    NOT NULL UNIQUE,
    phone           VARCHAR(20),
    hashed_password VARCHAR(255)    NOT NULL,
    full_name       VARCHAR(255)    NOT NULL,
    role            user_role       NOT NULL,
    status          account_status  NOT NULL DEFAULT 'active',
    region_id       VARCHAR(36),
    school_id       VARCHAR(36),
    merchant_id     VARCHAR(36),
    is_active       BOOLEAN         NOT NULL DEFAULT TRUE,
    last_login_at   TIMESTAMPTZ,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ
);

-- ── 2. regions ───────────────────────────────────────────────
CREATE TABLE regions (
    id          VARCHAR(36)     PRIMARY KEY DEFAULT gen_random_uuid()::text,
    region_code VARCHAR(50)     NOT NULL UNIQUE,
    region_name VARCHAR(255)    NOT NULL,
    province    VARCHAR(255),
    admin_user_id VARCHAR(36),
    status      region_status   NOT NULL DEFAULT 'active',
    created_by  VARCHAR(36),
    created_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

-- ── 3. schools ───────────────────────────────────────────────
CREATE TABLE schools (
    id          VARCHAR(36)     PRIMARY KEY DEFAULT gen_random_uuid()::text,
    region_id   VARCHAR(36)     NOT NULL REFERENCES regions(id),
    school_code VARCHAR(50)     NOT NULL UNIQUE,
    school_name VARCHAR(255)    NOT NULL,
    address     TEXT,
    city        VARCHAR(255),
    admin_user_id VARCHAR(36),
    school_type school_type,
    status      school_status   NOT NULL DEFAULT 'pending_approval',
    approved_by VARCHAR(36),
    created_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

-- ── 4. merchants ─────────────────────────────────────────────
CREATE TABLE merchants (
    id            VARCHAR(36)     PRIMARY KEY DEFAULT gen_random_uuid()::text,
    user_id       VARCHAR(36)     REFERENCES users(id),
    school_id     VARCHAR(36)     NOT NULL REFERENCES schools(id),
    business_name VARCHAR(255)    NOT NULL,
    business_type business_type   NOT NULL DEFAULT 'kantin',
    owner_name    VARCHAR(255),
    phone         VARCHAR(20),
    email         VARCHAR(255),
    address       TEXT,
    logo_url      VARCHAR(500),
    balance       NUMERIC(15,2)   NOT NULL DEFAULT 0.00,
    status        merchant_status NOT NULL DEFAULT 'active',
    created_at    TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

-- ── 5. parents ───────────────────────────────────────────────
CREATE TABLE parents (
    id                  VARCHAR(36)     PRIMARY KEY DEFAULT gen_random_uuid()::text,
    user_id             VARCHAR(36)     REFERENCES users(id),
    school_id           VARCHAR(36)     NOT NULL REFERENCES schools(id),
    name                VARCHAR(255)    NOT NULL,
    phone               VARCHAR(20),
    email               VARCHAR(255),
    daily_limit_default NUMERIC(15,2)   NOT NULL DEFAULT 50000.00,
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

-- ── 6. clients ───────────────────────────────────────────────
CREATE TABLE clients (
    id                      VARCHAR(36)     PRIMARY KEY DEFAULT gen_random_uuid()::text,
    user_id                 VARCHAR(36)     REFERENCES users(id),
    parent_id               VARCHAR(36)     NOT NULL REFERENCES parents(id),
    school_id               VARCHAR(36)     NOT NULL REFERENCES schools(id),
    name                    VARCHAR(255)    NOT NULL,
    student_id_number       VARCHAR(50),
    class_name              VARCHAR(50),
    grade                   VARCHAR(20),
    daily_spending_limit    NUMERIC(15,2),
    biometric_enrolled      BOOLEAN         NOT NULL DEFAULT FALSE,
    biometric_last_updated  TIMESTAMPTZ,
    balance                 NUMERIC(15,2)   NOT NULL DEFAULT 0.00,
    pin_hash                VARCHAR(255),
    status                  client_status   NOT NULL DEFAULT 'active',
    photo_url               VARCHAR(500),
    created_at              TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

-- ── 7. devices ───────────────────────────────────────────────
CREATE TABLE devices (
    id               VARCHAR(36)     PRIMARY KEY DEFAULT gen_random_uuid()::text,
    device_serial    VARCHAR(100)    NOT NULL UNIQUE,
    school_id        VARCHAR(36)     REFERENCES schools(id),
    merchant_id      VARCHAR(36)     REFERENCES merchants(id),
    device_type      device_type     NOT NULL DEFAULT 'combo_device',
    name             VARCHAR(255),
    license_key      VARCHAR(100)    UNIQUE,
    firmware_version VARCHAR(50),
    sdk_version      VARCHAR(50),
    mac_address      VARCHAR(17),
    ip_address       VARCHAR(45),
    status           device_status   NOT NULL DEFAULT 'registered',
    is_active        BOOLEAN         NOT NULL DEFAULT TRUE,
    last_heartbeat   TIMESTAMPTZ,
    config_json      TEXT,
    created_at       TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

-- ── 8. wallets ───────────────────────────────────────────────
CREATE TABLE wallets (
    id         VARCHAR(36)     PRIMARY KEY DEFAULT gen_random_uuid()::text,
    client_id  VARCHAR(36)     NOT NULL UNIQUE REFERENCES clients(id),
    balance    NUMERIC(15,2)   NOT NULL DEFAULT 0.00,
    status     wallet_status   NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

-- ── 9. wallet_ledger ─────────────────────────────────────────
CREATE TABLE wallet_ledger (
    id             VARCHAR(36)     PRIMARY KEY DEFAULT gen_random_uuid()::text,
    wallet_id      VARCHAR(36)     NOT NULL REFERENCES wallets(id),
    type           ledger_type     NOT NULL,
    amount         NUMERIC(15,2)   NOT NULL,
    balance_before NUMERIC(15,2)   NOT NULL,
    balance_after  NUMERIC(15,2)   NOT NULL,
    reference_id   VARCHAR(36),
    description    TEXT,
    created_at     TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

-- ── 10. products ─────────────────────────────────────────────
CREATE TABLE products (
    id             VARCHAR(36)         PRIMARY KEY DEFAULT gen_random_uuid()::text,
    merchant_id    VARCHAR(36)         NOT NULL REFERENCES merchants(id),
    name           VARCHAR(255)        NOT NULL,
    description    TEXT,
    price          NUMERIC(15,2)       NOT NULL,
    category       product_category    NOT NULL DEFAULT 'lainnya',
    image_url      VARCHAR(500),
    is_available   BOOLEAN             NOT NULL DEFAULT TRUE,
    stock_quantity INTEGER,
    created_at     TIMESTAMPTZ         NOT NULL DEFAULT NOW(),
    updated_at     TIMESTAMPTZ         NOT NULL DEFAULT NOW()
);

-- ── 11. transactions ─────────────────────────────────────────
CREATE TABLE transactions (
    id                       VARCHAR(36)         PRIMARY KEY DEFAULT gen_random_uuid()::text,
    transaction_ref          VARCHAR(100)        NOT NULL UNIQUE,
    type                     transaction_type    NOT NULL,
    client_id                VARCHAR(36)         REFERENCES clients(id),
    merchant_id              VARCHAR(36)         REFERENCES merchants(id),
    parent_id                VARCHAR(36)         REFERENCES parents(id),
    school_id                VARCHAR(36)         REFERENCES schools(id),
    device_id                VARCHAR(36)         REFERENCES devices(id),
    amount                   NUMERIC(15,2)       NOT NULL,
    fee_amount               NUMERIC(15,2)       NOT NULL DEFAULT 0.00,
    status                   transaction_status  NOT NULL DEFAULT 'pending',
    payment_method           payment_method,
    biometric_method         biometric_method,
    confidence_score         FLOAT,
    offline_flag             BOOLEAN             NOT NULL DEFAULT FALSE,
    synced_at                TIMESTAMPTZ,
    rejection_reason         TEXT,
    metadata_json            TEXT,
    reference_transaction_id VARCHAR(36),
    created_at               TIMESTAMPTZ         NOT NULL DEFAULT NOW(),
    completed_at             TIMESTAMPTZ
);

-- ── 12. transaction_items ────────────────────────────────────
CREATE TABLE transaction_items (
    id             VARCHAR(36)     PRIMARY KEY DEFAULT gen_random_uuid()::text,
    transaction_id VARCHAR(36)     NOT NULL REFERENCES transactions(id),
    product_id     VARCHAR(36)     REFERENCES products(id),
    product_name   VARCHAR(255)    NOT NULL,
    quantity       INTEGER         NOT NULL DEFAULT 1,
    unit_price     NUMERIC(15,2)   NOT NULL,
    subtotal       NUMERIC(15,2)   NOT NULL
);

-- ── 13. face_credentials ─────────────────────────────────────
CREATE TABLE face_credentials (
    id                 VARCHAR(36)         PRIMARY KEY DEFAULT gen_random_uuid()::text,
    client_id          VARCHAR(36)         NOT NULL UNIQUE REFERENCES clients(id),
    embedding          BYTEA               NOT NULL,
    embedding_version  VARCHAR(50)         NOT NULL DEFAULT 'arcface_r100',
    quality_score      FLOAT,
    status             credential_status   NOT NULL DEFAULT 'active',
    enrolled_by        VARCHAR(36),
    enrolled_at        TIMESTAMPTZ         NOT NULL DEFAULT NOW(),
    updated_at         TIMESTAMPTZ         NOT NULL DEFAULT NOW()
);

-- ── 14. fingerprint_credentials ──────────────────────────────
CREATE TABLE fingerprint_credentials (
    id            VARCHAR(36)         PRIMARY KEY DEFAULT gen_random_uuid()::text,
    client_id     VARCHAR(36)         NOT NULL UNIQUE REFERENCES clients(id),
    template_data BYTEA               NOT NULL,
    finger_index  INTEGER             NOT NULL DEFAULT 1,
    quality_score FLOAT,
    status        credential_status   NOT NULL DEFAULT 'active',
    enrolled_by   VARCHAR(36),
    enrolled_at   TIMESTAMPTZ         NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ         NOT NULL DEFAULT NOW()
);

-- ── 15. tickets ──────────────────────────────────────────────
CREATE TABLE tickets (
    id            VARCHAR(36)         PRIMARY KEY DEFAULT gen_random_uuid()::text,
    ticket_number VARCHAR(50)         NOT NULL UNIQUE,
    created_by    VARCHAR(36)         NOT NULL REFERENCES users(id),
    assigned_to   VARCHAR(36)         REFERENCES users(id),
    school_id     VARCHAR(36)         REFERENCES schools(id),
    category      ticket_category     NOT NULL DEFAULT 'other',
    subject       VARCHAR(255)        NOT NULL,
    description   TEXT,
    status        ticket_status       NOT NULL DEFAULT 'open',
    priority      ticket_priority     NOT NULL DEFAULT 'medium',
    sla_deadline  TIMESTAMPTZ,
    resolved_at   TIMESTAMPTZ,
    created_at    TIMESTAMPTZ         NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ         NOT NULL DEFAULT NOW()
);

-- ── 16. approval_requests ────────────────────────────────────
CREATE TABLE approval_requests (
    id            VARCHAR(36)             PRIMARY KEY DEFAULT gen_random_uuid()::text,
    request_type  approval_request_type   NOT NULL,
    requestor_id  VARCHAR(36)             NOT NULL REFERENCES users(id),
    approver_id   VARCHAR(36)             REFERENCES users(id),
    entity_type   VARCHAR(100),
    entity_data   TEXT,
    status        approval_status         NOT NULL DEFAULT 'pending',
    requested_at  TIMESTAMPTZ             NOT NULL DEFAULT NOW(),
    decided_at    TIMESTAMPTZ,
    decision_note TEXT
);

-- ── 17. audit_logs ───────────────────────────────────────────
CREATE TABLE audit_logs (
    id          VARCHAR(36)         PRIMARY KEY DEFAULT gen_random_uuid()::text,
    timestamp   TIMESTAMPTZ         NOT NULL DEFAULT NOW(),
    event_type  audit_event_type    NOT NULL,
    actor_id    VARCHAR(36),
    actor_role  VARCHAR(50),
    target_id   VARCHAR(36),
    action      VARCHAR(255)        NOT NULL,
    details     TEXT,
    ip_address  VARCHAR(45),
    device_info VARCHAR(500),
    result      audit_result        NOT NULL DEFAULT 'success',
    school_id   VARCHAR(36)
);

-- ── 18. notifications ────────────────────────────────────────
CREATE TABLE notifications (
    id                VARCHAR(36)         PRIMARY KEY DEFAULT gen_random_uuid()::text,
    recipient_user_id VARCHAR(36)         NOT NULL REFERENCES users(id),
    notification_type notification_type   NOT NULL,
    title             VARCHAR(255)        NOT NULL,
    message           TEXT                NOT NULL,
    reference_type    VARCHAR(100),
    reference_id      VARCHAR(36),
    is_read           BOOLEAN             NOT NULL DEFAULT FALSE,
    created_at        TIMESTAMPTZ         NOT NULL DEFAULT NOW()
);

-- ── 19. firmware_versions ────────────────────────────────────
CREATE TABLE firmware_versions (
    id          VARCHAR(36)     PRIMARY KEY DEFAULT gen_random_uuid()::text,
    version     VARCHAR(50)     NOT NULL UNIQUE,
    description TEXT,
    file_url    VARCHAR(500)    NOT NULL,
    file_size   INTEGER,
    checksum    VARCHAR(64),
    is_stable   BOOLEAN         NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

-- ============================================================
--  INDEXES
-- ============================================================

-- users
CREATE INDEX idx_users_email       ON users(email);
CREATE INDEX idx_users_role        ON users(role);
CREATE INDEX idx_users_school_id   ON users(school_id);

-- schools
CREATE INDEX idx_schools_region_id ON schools(region_id);
CREATE INDEX idx_schools_status    ON schools(status);

-- merchants
CREATE INDEX idx_merchants_school_id ON merchants(school_id);
CREATE INDEX idx_merchants_status    ON merchants(status);

-- parents
CREATE INDEX idx_parents_school_id ON parents(school_id);
CREATE INDEX idx_parents_user_id   ON parents(user_id);

-- clients
CREATE INDEX idx_clients_parent_id ON clients(parent_id);
CREATE INDEX idx_clients_school_id ON clients(school_id);
CREATE INDEX idx_clients_status    ON clients(status);

-- devices
CREATE INDEX idx_devices_license_key  ON devices(license_key);
CREATE INDEX idx_devices_merchant_id  ON devices(merchant_id);
CREATE INDEX idx_devices_school_id    ON devices(school_id);

-- wallets
CREATE INDEX idx_wallet_ledger_wallet_id   ON wallet_ledger(wallet_id);
CREATE INDEX idx_wallet_ledger_created_at  ON wallet_ledger(created_at DESC);

-- transactions
CREATE INDEX idx_transactions_client_id   ON transactions(client_id);
CREATE INDEX idx_transactions_merchant_id ON transactions(merchant_id);
CREATE INDEX idx_transactions_school_id   ON transactions(school_id);
CREATE INDEX idx_transactions_status      ON transactions(status);
CREATE INDEX idx_transactions_created_at  ON transactions(created_at DESC);

-- audit_logs
CREATE INDEX idx_audit_logs_actor_id   ON audit_logs(actor_id);
CREATE INDEX idx_audit_logs_timestamp  ON audit_logs(timestamp DESC);
CREATE INDEX idx_audit_logs_school_id  ON audit_logs(school_id);

-- notifications
CREATE INDEX idx_notifications_recipient ON notifications(recipient_user_id);
CREATE INDEX idx_notifications_is_read   ON notifications(recipient_user_id, is_read);

-- tickets
CREATE INDEX idx_tickets_status      ON tickets(status);
CREATE INDEX idx_tickets_school_id   ON tickets(school_id);
CREATE INDEX idx_tickets_assigned_to ON tickets(assigned_to);
