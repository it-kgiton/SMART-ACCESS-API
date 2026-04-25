-- ============================================================
--  Smart Access — Supabase Storage Buckets
--  Run this manually in Supabase SQL Editor
--  Requires: Supabase project with Storage enabled
-- ============================================================

-- ── Firmware bucket (OTA update files for ESP32 devices) ────
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'firmware',
    'firmware',
    FALSE,
    10485760,  -- 10 MB max per file
    ARRAY['application/octet-stream', 'application/zip', 'application/x-binary']
)
ON CONFLICT (id) DO NOTHING;

-- ── Biometric assets bucket (face images, enrollment data) ──
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'biometric-assets',
    'biometric-assets',
    FALSE,
    5242880,  -- 5 MB max per file
    ARRAY['image/jpeg', 'image/png', 'image/webp', 'application/octet-stream']
)
ON CONFLICT (id) DO NOTHING;

-- ============================================================
--  Storage RLS Policies
-- ============================================================

-- firmware: hanya service role yang bisa upload/download
CREATE POLICY "Service role only — firmware"
ON storage.objects FOR ALL
USING (
    bucket_id = 'firmware'
    AND auth.role() = 'service_role'
);

-- biometric-assets: hanya service role yang bisa akses
CREATE POLICY "Service role only — biometric-assets"
ON storage.objects FOR ALL
USING (
    bucket_id = 'biometric-assets'
    AND auth.role() = 'service_role'
);
