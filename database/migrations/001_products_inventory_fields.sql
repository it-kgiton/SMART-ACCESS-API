-- ============================================================
--  Migration 001 — Add inventory fields to products table
--  Tanggal : 2026-05-05
--  Deskripsi: Tambah kolom sku, cost_price, min_stock,
--             stock_alert_threshold untuk fitur Inventory
--             Management merchant.
--
--  Jalankan di Supabase SQL Editor atau psql:
--    psql $DATABASE_URL -f database/migrations/001_products_inventory_fields.sql
-- ============================================================

ALTER TABLE products
    ADD COLUMN IF NOT EXISTS sku                   VARCHAR(100),
    ADD COLUMN IF NOT EXISTS cost_price            NUMERIC(15,2),
    ADD COLUMN IF NOT EXISTS min_stock             INTEGER,
    ADD COLUMN IF NOT EXISTS stock_alert_threshold INTEGER;
