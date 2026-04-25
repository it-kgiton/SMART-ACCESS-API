-- ============================================================
--  Smart Access — Reset Database
--  WARNING: Menghapus SEMUA tabel, enum, dan index!
--  Jalankan ini hanya di development / staging.
--  Setelah ini jalankan schema.sql untuk rebuild dari awal.
-- ============================================================

-- ── Drop tables (urutan terbalik dari schema.sql) ────────────
DROP TABLE IF EXISTS firmware_versions        CASCADE;
DROP TABLE IF EXISTS notifications             CASCADE;
DROP TABLE IF EXISTS audit_logs               CASCADE;
DROP TABLE IF EXISTS approval_requests        CASCADE;
DROP TABLE IF EXISTS tickets                  CASCADE;
DROP TABLE IF EXISTS fingerprint_credentials  CASCADE;
DROP TABLE IF EXISTS face_credentials         CASCADE;
DROP TABLE IF EXISTS transaction_items        CASCADE;
DROP TABLE IF EXISTS transactions             CASCADE;
DROP TABLE IF EXISTS products                 CASCADE;
DROP TABLE IF EXISTS wallet_ledger            CASCADE;
DROP TABLE IF EXISTS wallets                  CASCADE;
DROP TABLE IF EXISTS devices                  CASCADE;
DROP TABLE IF EXISTS clients                  CASCADE;
DROP TABLE IF EXISTS parents                  CASCADE;
DROP TABLE IF EXISTS merchants                CASCADE;
DROP TABLE IF EXISTS schools                  CASCADE;
DROP TABLE IF EXISTS regions                  CASCADE;
DROP TABLE IF EXISTS users                    CASCADE;

-- ── Drop enum types ──────────────────────────────────────────
DROP TYPE IF EXISTS notification_type         CASCADE;
DROP TYPE IF EXISTS audit_result              CASCADE;
DROP TYPE IF EXISTS audit_event_type          CASCADE;
DROP TYPE IF EXISTS approval_status           CASCADE;
DROP TYPE IF EXISTS approval_request_type     CASCADE;
DROP TYPE IF EXISTS ticket_status             CASCADE;
DROP TYPE IF EXISTS ticket_priority           CASCADE;
DROP TYPE IF EXISTS ticket_category           CASCADE;
DROP TYPE IF EXISTS product_category          CASCADE;
DROP TYPE IF EXISTS credential_status         CASCADE;
DROP TYPE IF EXISTS biometric_method          CASCADE;
DROP TYPE IF EXISTS payment_method            CASCADE;
DROP TYPE IF EXISTS transaction_status        CASCADE;
DROP TYPE IF EXISTS transaction_type          CASCADE;
DROP TYPE IF EXISTS ledger_type               CASCADE;
DROP TYPE IF EXISTS wallet_status             CASCADE;
DROP TYPE IF EXISTS device_status             CASCADE;
DROP TYPE IF EXISTS device_type               CASCADE;
DROP TYPE IF EXISTS client_status             CASCADE;
DROP TYPE IF EXISTS merchant_status           CASCADE;
DROP TYPE IF EXISTS business_type             CASCADE;
DROP TYPE IF EXISTS school_status             CASCADE;
DROP TYPE IF EXISTS school_type               CASCADE;
DROP TYPE IF EXISTS region_status             CASCADE;
DROP TYPE IF EXISTS account_status            CASCADE;
DROP TYPE IF EXISTS user_role                 CASCADE;
