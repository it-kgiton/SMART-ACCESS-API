-- ============================================================
--  Smart Access — Supabase Storage Buckets
--  Run this manually in Supabase SQL Editor
--  Requires: Supabase project with Storage enabled
--
--  Naming convention: smart-access-<purpose>
-- ============================================================

-- ── Firmware bucket (OTA update files for ESP32 devices) ────
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'smart-access-firmware',
    'smart-access-firmware',
    FALSE,
    10485760,  -- 10 MB max per file
    ARRAY['application/octet-stream', 'application/zip', 'application/x-binary']
)
ON CONFLICT (id) DO NOTHING;

-- ── Biometric assets bucket (face images, enrollment data) ──
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'smart-access-biometric',
    'smart-access-biometric',
    FALSE,
    5242880,  -- 5 MB max per file
    ARRAY['image/jpeg', 'image/png', 'image/webp', 'application/octet-stream']
)
ON CONFLICT (id) DO NOTHING;

-- ── Merchant assets bucket (logo merchant) ──────────────────
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'smart-access-merchant',
    'smart-access-merchant',
    TRUE,
    2097152,  -- 2 MB max per file
    ARRAY['image/jpeg', 'image/png', 'image/webp']
)
ON CONFLICT (id) DO NOTHING;

-- ── Product assets bucket (foto produk) ─────────────────────
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'smart-access-product',
    'smart-access-product',
    TRUE,
    2097152,  -- 2 MB max per file
    ARRAY['image/jpeg', 'image/png', 'image/webp']
)
ON CONFLICT (id) DO NOTHING;

-- ============================================================
--  Storage RLS Policies
-- ============================================================

-- smart-access-firmware: hanya service role yang bisa upload/download
CREATE POLICY "Service role only — smart-access-firmware"
ON storage.objects FOR ALL
USING (
    bucket_id = 'smart-access-firmware'
    AND auth.role() = 'service_role'
);

-- smart-access-biometric: hanya service role yang bisa akses
CREATE POLICY "Service role only — smart-access-biometric"
ON storage.objects FOR ALL
USING (
    bucket_id = 'smart-access-biometric'
    AND auth.role() = 'service_role'
);

-- smart-access-merchant: public read, service role write
CREATE POLICY "Public read — smart-access-merchant"
ON storage.objects FOR SELECT
USING (bucket_id = 'smart-access-merchant');

CREATE POLICY "Service role write — smart-access-merchant"
ON storage.objects FOR INSERT
WITH CHECK (
    bucket_id = 'smart-access-merchant'
    AND auth.role() = 'service_role'
);

-- smart-access-product: public read, service role write
CREATE POLICY "Public read — smart-access-product"
ON storage.objects FOR SELECT
USING (bucket_id = 'smart-access-product');

CREATE POLICY "Service role write — smart-access-product"
ON storage.objects FOR INSERT
WITH CHECK (
    bucket_id = 'smart-access-product'
    AND auth.role() = 'service_role'
);
