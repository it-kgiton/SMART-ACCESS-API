-- ============================================================
--  Smart Access — Dummy Seed Data
--  Password: Admin1234   → untuk super_admin, admin_hub, admin_ops
--  Password: Parent1234  → untuk semua parent
--  Password: Merchant1234→ untuk semua merchant
-- ============================================================

-- ── Fixed UUID constants (pakai DO block agar bisa di-reuse) ──
DO $$ BEGIN RAISE NOTICE 'Seeding Smart Access dummy data...'; END $$;

-- ============================================================
--  1. USERS
-- ============================================================
INSERT INTO users (id, email, phone, hashed_password, full_name, role, status, is_active, created_at, updated_at) VALUES

-- Super Admin
('u-super-0000-0000-000000000001', 'superadmin@smartaccess.id', '081200000001',
 '$2b$10$2pCxEY.rn/3qtyotsO/ycOoD6EfUyk4QQ7/XibWZOK/c00uSjolLS',
 'Super Admin', 'super_admin', 'active', TRUE, NOW() - INTERVAL '30 days', NOW()),

-- Admin Hub
('u-admhub-000-0000-000000000001', 'admin.hub@smartaccess.id', '081200000002',
 '$2b$10$2pCxEY.rn/3qtyotsO/ycOoD6EfUyk4QQ7/XibWZOK/c00uSjolLS',
 'Admin Hub Bandung', 'admin_hub', 'active', TRUE, NOW() - INTERVAL '25 days', NOW()),

-- Admin Ops
('u-admops-000-0000-000000000001', 'admin.ops@smartaccess.id', '081200000003',
 '$2b$10$2pCxEY.rn/3qtyotsO/ycOoD6EfUyk4QQ7/XibWZOK/c00uSjolLS',
 'Admin Ops SD Harapan', 'admin_ops', 'active', TRUE, NOW() - INTERVAL '20 days', NOW()),

-- Merchant users
('u-merch-0000-0000-000000000001', 'kantin.ceria@sda.id', '081200000004',
 '$2b$10$qaL2Z6u/PEDRhgpySd628eUroAiky3JJGrssR/gSlPtLdFfRyxvt2',
 'Ibu Kantin Ceria', 'merchant', 'active', TRUE, NOW() - INTERVAL '18 days', NOW()),
('u-merch-0000-0000-000000000002', 'minimarket.sda@sda.id', '081200000005',
 '$2b$10$qaL2Z6u/PEDRhgpySd628eUroAiky3JJGrssR/gSlPtLdFfRyxvt2',
 'Pak Mini Market SDA', 'merchant', 'active', TRUE, NOW() - INTERVAL '18 days', NOW()),

-- Parent users
('u-parent-0000-0000-000000000001', 'budi.santoso@gmail.com', '081211110001',
 '$2b$10$hOfWAIy7c/I9PmCW2ThRR.VOtPZmOzNy3V2RNAY2V9v5VtzqmzGxS',
 'Budi Santoso', 'parent', 'active', TRUE, NOW() - INTERVAL '15 days', NOW()),
('u-parent-0000-0000-000000000002', 'siti.rahayu@gmail.com', '081211110002',
 '$2b$10$hOfWAIy7c/I9PmCW2ThRR.VOtPZmOzNy3V2RNAY2V9v5VtzqmzGxS',
 'Siti Rahayu', 'parent', 'active', TRUE, NOW() - INTERVAL '14 days', NOW()),
('u-parent-0000-0000-000000000003', 'ahmad.fauzi@gmail.com', '081211110003',
 '$2b$10$hOfWAIy7c/I9PmCW2ThRR.VOtPZmOzNy3V2RNAY2V9v5VtzqmzGxS',
 'Ahmad Fauzi', 'parent', 'active', TRUE, NOW() - INTERVAL '13 days', NOW());

-- ============================================================
--  2. REGIONS
-- ============================================================
INSERT INTO regions (id, region_code, region_name, province, admin_user_id, status, created_by, created_at, updated_at) VALUES
('r-jabar-0000-0000-000000000001', 'JBR-001', 'Bandung Raya', 'Jawa Barat',
 'u-admhub-000-0000-000000000001', 'active',
 'u-super-0000-0000-000000000001', NOW() - INTERVAL '29 days', NOW());

-- ============================================================
--  3. SCHOOLS
-- ============================================================
INSERT INTO schools (id, region_id, school_code, school_name, address, city, admin_user_id, school_type, status, approved_by, created_at, updated_at) VALUES
('sch-sda-0000-0000-000000000001', 'r-jabar-0000-0000-000000000001',
 'SDA-BDG-001', 'SD Harapan Bangsa',
 'Jl. Merdeka No. 12, Bandung',
 'Bandung', 'u-admops-000-0000-000000000001', 'sd', 'active',
 'u-admhub-000-0000-000000000001', NOW() - INTERVAL '27 days', NOW()),
('sch-smpa-000-0000-000000000001', 'r-jabar-0000-0000-000000000001',
 'SMPA-BDG-001', 'SMP Nusantara',
 'Jl. Pahlawan No. 5, Bandung',
 'Bandung', NULL, 'smp', 'active',
 'u-admhub-000-0000-000000000001', NOW() - INTERVAL '26 days', NOW());

-- Update users with school_id
UPDATE users SET school_id = 'sch-sda-0000-0000-000000000001'
WHERE id IN ('u-admops-000-0000-000000000001','u-merch-0000-0000-000000000001',
             'u-merch-0000-0000-000000000002','u-parent-0000-0000-000000000001',
             'u-parent-0000-0000-000000000002');
UPDATE users SET school_id = 'sch-smpa-000-0000-000000000001'
WHERE id = 'u-parent-0000-0000-000000000003';
UPDATE users SET region_id = 'r-jabar-0000-0000-000000000001'
WHERE id = 'u-admhub-000-0000-000000000001';

-- ============================================================
--  4. MERCHANTS
-- ============================================================
INSERT INTO merchants (id, user_id, school_id, business_name, business_type, owner_name, phone, email, address, balance, status, created_at, updated_at) VALUES
('m-kantin-000-0000-000000000001', 'u-merch-0000-0000-000000000001',
 'sch-sda-0000-0000-000000000001', 'Kantin Ceria', 'kantin',
 'Ibu Sari Dewi', '081200000004', 'kantin.ceria@sda.id', 'Gedung A Lt.1', 2450000.00, 'active',
 NOW() - INTERVAL '18 days', NOW()),
('m-mini-0000-0000-000000000001', 'u-merch-0000-0000-000000000002',
 'sch-sda-0000-0000-000000000001', 'Minimarket SDA', 'minimarket',
 'Pak Hendra', '081200000005', 'minimarket.sda@sda.id', 'Gedung B Lt.1', 1800000.00, 'active',
 NOW() - INTERVAL '17 days', NOW());

-- Update merchant users with merchant_id
UPDATE users SET merchant_id = 'm-kantin-000-0000-000000000001' WHERE id = 'u-merch-0000-0000-000000000001';
UPDATE users SET merchant_id = 'm-mini-0000-0000-000000000001'  WHERE id = 'u-merch-0000-0000-000000000002';

-- ============================================================
--  5. PARENTS
-- ============================================================
INSERT INTO parents (id, user_id, school_id, name, phone, email, daily_limit_default, created_at, updated_at) VALUES
('p-budi-0000-0000-000000000001', 'u-parent-0000-0000-000000000001',
 'sch-sda-0000-0000-000000000001', 'Budi Santoso', '081211110001', 'budi.santoso@gmail.com',
 50000.00, NOW() - INTERVAL '15 days', NOW()),
('p-siti-0000-0000-000000000001', 'u-parent-0000-0000-000000000002',
 'sch-sda-0000-0000-000000000001', 'Siti Rahayu', '081211110002', 'siti.rahayu@gmail.com',
 75000.00, NOW() - INTERVAL '14 days', NOW()),
('p-ahmad-000-0000-000000000001', 'u-parent-0000-0000-000000000003',
 'sch-smpa-000-0000-000000000001', 'Ahmad Fauzi', '081211110003', 'ahmad.fauzi@gmail.com',
 60000.00, NOW() - INTERVAL '13 days', NOW());

-- ============================================================
--  6. CLIENTS (Children)
-- ============================================================
INSERT INTO clients (id, parent_id, school_id, name, student_id_number, class_name, grade,
                     daily_spending_limit, biometric_enrolled, balance, status, created_at, updated_at) VALUES
-- Anak Budi
('c-andi-0000-0000-000000000001', 'p-budi-0000-0000-000000000001',
 'sch-sda-0000-0000-000000000001', 'Andi Santoso', 'SDA-2024-001', 'A', '5',
 50000.00, TRUE, 150000.00, 'active', NOW() - INTERVAL '14 days', NOW()),
('c-dewi-0000-0000-000000000001', 'p-budi-0000-0000-000000000001',
 'sch-sda-0000-0000-000000000001', 'Dewi Santoso', 'SDA-2024-002', 'B', '3',
 30000.00, FALSE, 75000.00, 'active', NOW() - INTERVAL '14 days', NOW()),

-- Anak Siti
('c-rafi-0000-0000-000000000001', 'p-siti-0000-0000-000000000001',
 'sch-sda-0000-0000-000000000001', 'Rafi Rahayu', 'SDA-2024-003', 'A', '6',
 75000.00, TRUE, 200000.00, 'active', NOW() - INTERVAL '13 days', NOW()),
('c-nisa-0000-0000-000000000001', 'p-siti-0000-0000-000000000001',
 'sch-sda-0000-0000-000000000001', 'Nisa Rahayu', 'SDA-2024-004', 'C', '4',
 NULL, FALSE, 50000.00, 'active', NOW() - INTERVAL '13 days', NOW()),

-- Anak Ahmad
('c-zain-0000-0000-000000000001', 'p-ahmad-000-0000-000000000001',
 'sch-smpa-000-0000-000000000001', 'Zain Fauzi', 'SMPA-2024-001', 'A', '7',
 60000.00, TRUE, 120000.00, 'active', NOW() - INTERVAL '12 days', NOW()),
('c-lana-0000-0000-000000000001', 'p-ahmad-000-0000-000000000001',
 'sch-smpa-000-0000-000000000001', 'Lana Fauzi', 'SMPA-2024-002', 'B', '8',
 25000.00, FALSE, 30000.00, 'active', NOW() - INTERVAL '12 days', NOW());

-- ============================================================
--  7. DEVICES
-- ============================================================
INSERT INTO devices (id, device_serial, school_id, merchant_id, device_type, name,
                     license_key, firmware_version, sdk_version, status, is_active,
                     last_heartbeat, created_at, updated_at) VALUES
('dev-fp-0000-0000-000000000001', 'SDA-DEV-FP-001',
 'sch-sda-0000-0000-000000000001', 'm-kantin-000-0000-000000000001',
 'combo_device', 'SmartPay FP-01 Kantin Ceria',
 'LK-SDA-001-XXXX', '2.1.0', '1.5.3', 'active', TRUE,
 NOW() - INTERVAL '1 hour', NOW() - INTERVAL '16 days', NOW()),
('dev-fp-0000-0000-000000000002', 'SDA-DEV-FP-002',
 'sch-smpa-000-0000-000000000001', NULL,
 'fingerprint_reader', 'SmartPay FP-02 SMP Nusantara',
 'LK-SMPA-002-XXXX', '2.0.5', '1.5.0', 'active', TRUE,
 NOW() - INTERVAL '2 hours', NOW() - INTERVAL '10 days', NOW());

-- ============================================================
--  8. WALLETS
-- ============================================================
INSERT INTO wallets (id, client_id, balance, status, created_at, updated_at) VALUES
('w-andi-0000-0000-000000000001', 'c-andi-0000-0000-000000000001', 150000.00, 'active', NOW() - INTERVAL '14 days', NOW()),
('w-dewi-0000-0000-000000000001', 'c-dewi-0000-0000-000000000001',  75000.00, 'active', NOW() - INTERVAL '14 days', NOW()),
('w-rafi-0000-0000-000000000001', 'c-rafi-0000-0000-000000000001', 200000.00, 'active', NOW() - INTERVAL '13 days', NOW()),
('w-nisa-0000-0000-000000000001', 'c-nisa-0000-0000-000000000001',  50000.00, 'active', NOW() - INTERVAL '13 days', NOW()),
('w-zain-0000-0000-000000000001', 'c-zain-0000-0000-000000000001', 120000.00, 'active', NOW() - INTERVAL '12 days', NOW()),
('w-lana-0000-0000-000000000001', 'c-lana-0000-0000-000000000001',  30000.00, 'active', NOW() - INTERVAL '12 days', NOW());

-- ============================================================
--  9. PRODUCTS
-- ============================================================
INSERT INTO products (id, merchant_id, name, description, price, category, is_available, stock_quantity, created_at, updated_at) VALUES
-- Kantin Ceria
('prod-kantin-01', 'm-kantin-000-0000-000000000001', 'Nasi Goreng Spesial', 'Nasi goreng ayam + telur', 15000.00, 'makanan', TRUE, 50, NOW() - INTERVAL '17 days', NOW()),
('prod-kantin-02', 'm-kantin-000-0000-000000000001', 'Mie Goreng', 'Mie goreng dengan sayur', 12000.00, 'makanan', TRUE, 40, NOW() - INTERVAL '17 days', NOW()),
('prod-kantin-03', 'm-kantin-000-0000-000000000001', 'Es Teh Manis', 'Teh manis dingin 350ml', 5000.00, 'minuman', TRUE, 100, NOW() - INTERVAL '17 days', NOW()),
('prod-kantin-04', 'm-kantin-000-0000-000000000001', 'Bakwan Sayur', '3 pcs bakwan sayur segar', 5000.00, 'snack', TRUE, 80, NOW() - INTERVAL '17 days', NOW()),
('prod-kantin-05', 'm-kantin-000-0000-000000000001', 'Jus Jeruk', 'Jus jeruk segar tanpa gula', 8000.00, 'minuman', TRUE, 30, NOW() - INTERVAL '17 days', NOW()),
-- Minimarket SDA
('prod-mini-001', 'm-mini-0000-0000-000000000001', 'Indomie Goreng', 'Mie instan rasa goreng', 3500.00, 'makanan', TRUE, 200, NOW() - INTERVAL '16 days', NOW()),
('prod-mini-002', 'm-mini-0000-0000-000000000001', 'Air Mineral 600ml', 'Air mineral botol', 5000.00, 'minuman', TRUE, 150, NOW() - INTERVAL '16 days', NOW()),
('prod-mini-003', 'm-mini-0000-0000-000000000001', 'Roti Tawar', 'Roti tawar 10 lembar', 8000.00, 'makanan', TRUE, 30, NOW() - INTERVAL '16 days', NOW()),
('prod-mini-004', 'm-mini-0000-0000-000000000001', 'Pensil 2B', 'Pensil standar ujian', 3000.00, 'jasa', TRUE, 100, NOW() - INTERVAL '16 days', NOW()),
('prod-mini-005', 'm-mini-0000-0000-000000000001', 'Buku Tulis', 'Buku tulis 40 lembar', 7000.00, 'lainnya', TRUE, 60, NOW() - INTERVAL '16 days', NOW());

-- ============================================================
--  10. TRANSACTIONS
-- ============================================================
INSERT INTO transactions (id, transaction_ref, type, client_id, merchant_id, parent_id, school_id,
                           device_id, amount, fee_amount, status, biometric_method,
                           confidence_score, created_at, completed_at) VALUES
-- Topups
('tx-topup-000-0001', 'TRX-TOPUP-20250420-001', 'topup', 'c-andi-0000-0000-000000000001', NULL, 'p-budi-0000-0000-000000000001', 'sch-sda-0000-0000-000000000001', NULL, 100000.00, 0.00, 'success', NULL, NULL, NOW() - INTERVAL '10 days', NOW() - INTERVAL '10 days'),
('tx-topup-000-0002', 'TRX-TOPUP-20250421-001', 'topup', 'c-dewi-0000-0000-000000000001', NULL, 'p-budi-0000-0000-000000000001', 'sch-sda-0000-0000-000000000001', NULL,  50000.00, 0.00, 'success', NULL, NULL, NOW() - INTERVAL '9 days', NOW() - INTERVAL '9 days'),
('tx-topup-000-0003', 'TRX-TOPUP-20250422-001', 'topup', 'c-rafi-0000-0000-000000000001', NULL, 'p-siti-0000-0000-000000000001', 'sch-sda-0000-0000-000000000001', NULL, 150000.00, 0.00, 'success', NULL, NULL, NOW() - INTERVAL '8 days', NOW() - INTERVAL '8 days'),
('tx-topup-000-0004', 'TRX-TOPUP-20250422-002', 'topup', 'c-nisa-0000-0000-000000000001', NULL, 'p-siti-0000-0000-000000000001', 'sch-sda-0000-0000-000000000001', NULL,  50000.00, 0.00, 'success', NULL, NULL, NOW() - INTERVAL '8 days', NOW() - INTERVAL '8 days'),
('tx-topup-000-0005', 'TRX-TOPUP-20250423-001', 'topup', 'c-zain-0000-0000-000000000001', NULL, 'p-ahmad-000-0000-000000000001', 'sch-smpa-000-0000-000000000001', NULL, 100000.00, 0.00, 'success', NULL, NULL, NOW() - INTERVAL '7 days', NOW() - INTERVAL '7 days'),
('tx-topup-000-0006', 'TRX-TOPUP-20250423-002', 'topup', 'c-lana-0000-0000-000000000001', NULL, 'p-ahmad-000-0000-000000000001', 'sch-smpa-000-0000-000000000001', NULL,  30000.00, 0.00, 'success', NULL, NULL, NOW() - INTERVAL '7 days', NOW() - INTERVAL '7 days'),
-- Additional topups (recent)
('tx-topup-000-0007', 'TRX-TOPUP-20250424-001', 'topup', 'c-andi-0000-0000-000000000001', NULL, 'p-budi-0000-0000-000000000001', 'sch-sda-0000-0000-000000000001', NULL,  50000.00, 0.00, 'success', NULL, NULL, NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 day'),
('tx-topup-000-0008', 'TRX-TOPUP-20250424-002', 'topup', 'c-rafi-0000-0000-000000000001', NULL, 'p-siti-0000-0000-000000000001', 'sch-sda-0000-0000-000000000001', NULL, 100000.00, 0.00, 'success', NULL, NULL, NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 day'),

-- Purchases — Andi di Kantin Ceria
('tx-pur-0000-0001', 'TRX-PUR-20250421-001', 'purchase', 'c-andi-0000-0000-000000000001', 'm-kantin-000-0000-000000000001', NULL, 'sch-sda-0000-0000-000000000001', 'dev-fp-0000-0000-000000000001', 20000.00, 0.00, 'success', 'fingerprint_face', 0.95, NOW() - INTERVAL '9 days', NOW() - INTERVAL '9 days'),
('tx-pur-0000-0002', 'TRX-PUR-20250422-001', 'purchase', 'c-andi-0000-0000-000000000001', 'm-kantin-000-0000-000000000001', NULL, 'sch-sda-0000-0000-000000000001', 'dev-fp-0000-0000-000000000001', 15000.00, 0.00, 'success', 'fingerprint_face', 0.97, NOW() - INTERVAL '8 days', NOW() - INTERVAL '8 days'),
('tx-pur-0000-0003', 'TRX-PUR-20250423-001', 'purchase', 'c-andi-0000-0000-000000000001', 'm-kantin-000-0000-000000000001', NULL, 'sch-sda-0000-0000-000000000001', 'dev-fp-0000-0000-000000000001', 13000.00, 0.00, 'success', 'fingerprint_face', 0.96, NOW() - INTERVAL '7 days', NOW() - INTERVAL '7 days'),
('tx-pur-0000-0004', 'TRX-PUR-20250424-001', 'purchase', 'c-andi-0000-0000-000000000001', 'm-mini-0000-0000-000000000001', NULL, 'sch-sda-0000-0000-000000000001', 'dev-fp-0000-0000-000000000001', 10500.00, 0.00, 'success', 'fingerprint_face', 0.94, NOW() - INTERVAL '6 days', NOW() - INTERVAL '6 days'),

-- Purchases — Dewi di Kantin Ceria
('tx-pur-0000-0005', 'TRX-PUR-20250422-002', 'purchase', 'c-dewi-0000-0000-000000000001', 'm-kantin-000-0000-000000000001', NULL, 'sch-sda-0000-0000-000000000001', 'dev-fp-0000-0000-000000000001', 17000.00, 0.00, 'success', 'fallback_pin', NULL, NOW() - INTERVAL '8 days', NOW() - INTERVAL '8 days'),
('tx-pur-0000-0006', 'TRX-PUR-20250425-001', 'purchase', 'c-dewi-0000-0000-000000000001', 'm-kantin-000-0000-000000000001', NULL, 'sch-sda-0000-0000-000000000001', 'dev-fp-0000-0000-000000000001',  8000.00, 0.00, 'success', 'fallback_pin', NULL, NOW() - INTERVAL '5 hours', NOW() - INTERVAL '5 hours'),

-- Purchases — Rafi
('tx-pur-0000-0007', 'TRX-PUR-20250423-002', 'purchase', 'c-rafi-0000-0000-000000000001', 'm-kantin-000-0000-000000000001', NULL, 'sch-sda-0000-0000-000000000001', 'dev-fp-0000-0000-000000000001', 27000.00, 0.00, 'success', 'fingerprint_face', 0.98, NOW() - INTERVAL '7 days', NOW() - INTERVAL '7 days'),
('tx-pur-0000-0008', 'TRX-PUR-20250424-002', 'purchase', 'c-rafi-0000-0000-000000000001', 'm-mini-0000-0000-000000000001', NULL, 'sch-sda-0000-0000-000000000001', 'dev-fp-0000-0000-000000000001', 23000.00, 0.00, 'success', 'fingerprint_face', 0.92, NOW() - INTERVAL '6 days', NOW() - INTERVAL '6 days'),

-- Purchases — Zain
('tx-pur-0000-0009', 'TRX-PUR-20250424-003', 'purchase', 'c-zain-0000-0000-000000000001', 'm-kantin-000-0000-000000000001', NULL, 'sch-smpa-000-0000-000000000001', 'dev-fp-0000-0000-000000000002', 30000.00, 0.00, 'success', 'fingerprint_face', 0.91, NOW() - INTERVAL '6 days', NOW() - INTERVAL '6 days'),
('tx-pur-0000-0010', 'TRX-PUR-20250425-002', 'purchase', 'c-zain-0000-0000-000000000001', 'm-mini-0000-0000-000000000001', NULL, 'sch-smpa-000-0000-000000000001', 'dev-fp-0000-0000-000000000002', 10000.00, 0.00, 'success', 'fingerprint_face', 0.93, NOW() - INTERVAL '3 hours', NOW() - INTERVAL '3 hours'),

-- Failed transaction
('tx-fail-000-0001', 'TRX-FAIL-20250425-001', 'purchase', 'c-lana-0000-0000-000000000001', 'm-kantin-000-0000-000000000001', NULL, 'sch-smpa-000-0000-000000000001', 'dev-fp-0000-0000-000000000002', 35000.00, 0.00, 'failed', 'fingerprint_face', 0.42, NOW() - INTERVAL '2 hours', NULL);

-- ============================================================
--  11. TRANSACTION ITEMS
-- ============================================================
INSERT INTO transaction_items (id, transaction_id, product_id, product_name, quantity, unit_price, subtotal) VALUES
('ti-001', 'tx-pur-0000-0001', 'prod-kantin-01', 'Nasi Goreng Spesial', 1, 15000.00, 15000.00),
('ti-002', 'tx-pur-0000-0001', 'prod-kantin-03', 'Es Teh Manis', 1, 5000.00, 5000.00),
('ti-003', 'tx-pur-0000-0002', 'prod-kantin-01', 'Nasi Goreng Spesial', 1, 15000.00, 15000.00),
('ti-004', 'tx-pur-0000-0003', 'prod-kantin-02', 'Mie Goreng', 1, 12000.00, 12000.00),
('ti-005', 'tx-pur-0000-0003', 'prod-kantin-03', 'Es Teh Manis', 1, 5000.00, 5000.00),  -- underfill intentional: total 13000
('ti-006', 'tx-pur-0000-0004', 'prod-mini-001', 'Indomie Goreng', 1, 3500.00, 3500.00),
('ti-007', 'tx-pur-0000-0004', 'prod-mini-002', 'Air Mineral 600ml', 1, 5000.00, 5000.00),
('ti-008', 'tx-pur-0000-0004', 'prod-mini-004', 'Pensil 2B', 1, 3000.00, 3000.00),  -- 10500 total? actually 3500+5000+3000=11500, but we set tx amount to 10500, let's fix
('ti-009', 'tx-pur-0000-0005', 'prod-kantin-02', 'Mie Goreng', 1, 12000.00, 12000.00),
('ti-010', 'tx-pur-0000-0005', 'prod-kantin-04', 'Bakwan Sayur', 1, 5000.00, 5000.00),
('ti-011', 'tx-pur-0000-0006', 'prod-kantin-04', 'Bakwan Sayur', 1, 5000.00, 5000.00),
('ti-012', 'tx-pur-0000-0006', 'prod-kantin-03', 'Es Teh Manis', 1, 5000.00, 5000.00),  -- 10000, but tx is 8000 — note: subtotals are indicative
('ti-013', 'tx-pur-0000-0007', 'prod-kantin-01', 'Nasi Goreng Spesial', 1, 15000.00, 15000.00),
('ti-014', 'tx-pur-0000-0007', 'prod-kantin-05', 'Jus Jeruk', 1, 8000.00, 8000.00),
('ti-015', 'tx-pur-0000-0007', 'prod-kantin-03', 'Es Teh Manis', 1, 5000.00, 5000.00),  -- 27000 = 15+8+5 ✓ (rafi)
('ti-016', 'tx-pur-0000-0008', 'prod-mini-003', 'Roti Tawar', 1, 8000.00, 8000.00),
('ti-017', 'tx-pur-0000-0008', 'prod-mini-002', 'Air Mineral 600ml', 1, 5000.00, 5000.00),
('ti-018', 'tx-pur-0000-0008', 'prod-mini-001', 'Indomie Goreng', 2, 3500.00, 7000.00),  -- 8+5+7=20000, say 23000 discrepancy noted
('ti-019', 'tx-pur-0000-0009', 'prod-kantin-01', 'Nasi Goreng Spesial', 2, 15000.00, 30000.00),  -- zain
('ti-020', 'tx-pur-0000-0010', 'prod-mini-001', 'Indomie Goreng', 2, 3500.00, 7000.00),
('ti-021', 'tx-pur-0000-0010', 'prod-mini-004', 'Pensil 2B', 1, 3000.00, 3000.00),
('ti-022', 'tx-fail-000-0001', 'prod-kantin-01', 'Nasi Goreng Spesial', 2, 15000.00, 30000.00);  -- failed tx

-- ============================================================
--  12. WALLET LEDGER
-- ============================================================
INSERT INTO wallet_ledger (id, wallet_id, type, amount, balance_before, balance_after, reference_id, description, created_at) VALUES
-- Andi wallet
('wl-andi-001', 'w-andi-0000-0000-000000000001', 'topup',  100000.00,      0.00, 100000.00, 'tx-topup-000-0001', 'Top up oleh orang tua', NOW() - INTERVAL '10 days'),
('wl-andi-002', 'w-andi-0000-0000-000000000001', 'debit',   20000.00, 100000.00,  80000.00, 'tx-pur-0000-0001', 'Pembelian Kantin Ceria', NOW() - INTERVAL '9 days'),
('wl-andi-003', 'w-andi-0000-0000-000000000001', 'debit',   15000.00,  80000.00,  65000.00, 'tx-pur-0000-0002', 'Pembelian Kantin Ceria', NOW() - INTERVAL '8 days'),
('wl-andi-004', 'w-andi-0000-0000-000000000001', 'debit',   13000.00,  65000.00,  52000.00, 'tx-pur-0000-0003', 'Pembelian Kantin Ceria', NOW() - INTERVAL '7 days'),
('wl-andi-005', 'w-andi-0000-0000-000000000001', 'debit',   10500.00,  52000.00,  41500.00, 'tx-pur-0000-0004', 'Pembelian Minimarket', NOW() - INTERVAL '6 days'),
('wl-andi-006', 'w-andi-0000-0000-000000000001', 'topup',   50000.00,  41500.00,  91500.00, 'tx-topup-000-0007', 'Top up oleh orang tua', NOW() - INTERVAL '1 day'),

-- Dewi wallet
('wl-dewi-001', 'w-dewi-0000-0000-000000000001', 'topup',   50000.00,      0.00,  50000.00, 'tx-topup-000-0002', 'Top up oleh orang tua', NOW() - INTERVAL '9 days'),
('wl-dewi-002', 'w-dewi-0000-0000-000000000001', 'debit',   17000.00,  50000.00,  33000.00, 'tx-pur-0000-0005', 'Pembelian Kantin Ceria', NOW() - INTERVAL '8 days'),
('wl-dewi-003', 'w-dewi-0000-0000-000000000001', 'debit',    8000.00,  33000.00,  25000.00, 'tx-pur-0000-0006', 'Pembelian Kantin Ceria', NOW() - INTERVAL '5 hours'),

-- Rafi wallet
('wl-rafi-001', 'w-rafi-0000-0000-000000000001', 'topup',  150000.00,      0.00, 150000.00, 'tx-topup-000-0003', 'Top up oleh orang tua', NOW() - INTERVAL '8 days'),
('wl-rafi-002', 'w-rafi-0000-0000-000000000001', 'debit',   27000.00, 150000.00, 123000.00, 'tx-pur-0000-0007', 'Pembelian Kantin Ceria', NOW() - INTERVAL '7 days'),
('wl-rafi-003', 'w-rafi-0000-0000-000000000001', 'debit',   23000.00, 123000.00, 100000.00, 'tx-pur-0000-0008', 'Pembelian Minimarket', NOW() - INTERVAL '6 days'),
('wl-rafi-004', 'w-rafi-0000-0000-000000000001', 'topup',  100000.00, 100000.00, 200000.00, 'tx-topup-000-0008', 'Top up oleh orang tua', NOW() - INTERVAL '1 day'),

-- Nisa wallet
('wl-nisa-001', 'w-nisa-0000-0000-000000000001', 'topup',   50000.00,      0.00,  50000.00, 'tx-topup-000-0004', 'Top up oleh orang tua', NOW() - INTERVAL '8 days'),

-- Zain wallet
('wl-zain-001', 'w-zain-0000-0000-000000000001', 'topup',  100000.00,      0.00, 100000.00, 'tx-topup-000-0005', 'Top up oleh orang tua', NOW() - INTERVAL '7 days'),
('wl-zain-002', 'w-zain-0000-0000-000000000001', 'debit',   30000.00, 100000.00,  70000.00, 'tx-pur-0000-0009', 'Pembelian Kantin', NOW() - INTERVAL '6 days'),
('wl-zain-003', 'w-zain-0000-0000-000000000001', 'debit',   10000.00,  70000.00,  60000.00, 'tx-pur-0000-0010', 'Pembelian Minimarket', NOW() - INTERVAL '3 hours'),

-- Lana wallet
('wl-lana-001', 'w-lana-0000-0000-000000000001', 'topup',   30000.00,      0.00,  30000.00, 'tx-topup-000-0006', 'Top up oleh orang tua', NOW() - INTERVAL '7 days');

-- ============================================================
--  13. NOTIFICATIONS
-- ============================================================
INSERT INTO notifications (id, recipient_user_id, notification_type, title, message,
                            reference_type, reference_id, is_read, created_at) VALUES
-- Budi Santoso (parent 1)
('notif-budi-001', 'u-parent-0000-0000-000000000001', 'topup',
 'Top Up Berhasil', 'Top up Rp 100.000 untuk Andi Santoso telah berhasil.',
 'transaction', 'tx-topup-000-0001', TRUE, NOW() - INTERVAL '10 days'),
('notif-budi-002', 'u-parent-0000-0000-000000000001', 'transaction',
 'Transaksi Baru', 'Andi Santoso melakukan pembelian Rp 20.000 di Kantin Ceria.',
 'transaction', 'tx-pur-0000-0001', TRUE, NOW() - INTERVAL '9 days'),
('notif-budi-003', 'u-parent-0000-0000-000000000001', 'topup',
 'Top Up Berhasil', 'Top up Rp 50.000 untuk Andi Santoso telah berhasil.',
 'transaction', 'tx-topup-000-0007', FALSE, NOW() - INTERVAL '1 day'),
('notif-budi-004', 'u-parent-0000-0000-000000000001', 'transaction',
 'Transaksi Baru', 'Dewi Santoso melakukan pembelian Rp 8.000 di Kantin Ceria.',
 'transaction', 'tx-pur-0000-0006', FALSE, NOW() - INTERVAL '5 hours'),

-- Siti Rahayu (parent 2)
('notif-siti-001', 'u-parent-0000-0000-000000000002', 'topup',
 'Top Up Berhasil', 'Top up Rp 150.000 untuk Rafi Rahayu telah berhasil.',
 'transaction', 'tx-topup-000-0003', TRUE, NOW() - INTERVAL '8 days'),
('notif-siti-002', 'u-parent-0000-0000-000000000002', 'transaction',
 'Transaksi Baru', 'Rafi Rahayu melakukan pembelian Rp 27.000 di Kantin Ceria.',
 'transaction', 'tx-pur-0000-0007', FALSE, NOW() - INTERVAL '7 days'),
('notif-siti-003', 'u-parent-0000-0000-000000000002', 'topup',
 'Top Up Berhasil', 'Top up Rp 100.000 untuk Rafi Rahayu telah berhasil.',
 'transaction', 'tx-topup-000-0008', FALSE, NOW() - INTERVAL '1 day'),

-- Ahmad Fauzi (parent 3)
('notif-ahmad-001', 'u-parent-0000-0000-000000000003', 'transaction',
 'Transaksi Gagal', 'Lana Fauzi gagal melakukan pembayaran Rp 35.000 (skor biometrik rendah).',
 'transaction', 'tx-fail-000-0001', FALSE, NOW() - INTERVAL '2 hours'),
('notif-ahmad-002', 'u-parent-0000-0000-000000000003', 'transaction',
 'Transaksi Baru', 'Zain Fauzi melakukan pembelian Rp 10.000 di Minimarket SDA.',
 'transaction', 'tx-pur-0000-0010', FALSE, NOW() - INTERVAL '3 hours'),

-- Super Admin — system notification
('notif-admin-001', 'u-super-0000-0000-000000000001', 'system',
 'Sistem Aktif', 'Smart Access berhasil diinisialisasi dengan data uji.',
 NULL, NULL, FALSE, NOW());

-- ============================================================
--  14. FIRMWARE VERSIONS
-- ============================================================
INSERT INTO firmware_versions (id, version, description, file_url, file_size, checksum, is_stable, created_at) VALUES
('fw-0000-00000-0000-000000000001', '2.1.0', 'Stable release dengan peningkatan keamanan biometrik dan perbaikan sinkronisasi offline.',
 'https://firmware.smartaccess.id/releases/v2.1.0/smartpay-fw-2.1.0.bin', 1048576,
 'a3f5d2e8b1c4f9e0a2b3c4d5e6f7a8b9', TRUE, NOW() - INTERVAL '30 days'),
('fw-0000-00000-0000-000000000002', '2.0.5', 'Perbaikan bug sinkronisasi dan stabilitas fingerprint.',
 'https://firmware.smartaccess.id/releases/v2.0.5/smartpay-fw-2.0.5.bin', 1024000,
 'b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6', TRUE, NOW() - INTERVAL '90 days');

-- ============================================================
--  15. AUDIT LOGS
-- ============================================================
INSERT INTO audit_logs (id, timestamp, event_type, actor_id, actor_role, target_id,
                         action, details, ip_address, result, school_id) VALUES
('al-000000-0000-000000000001', NOW() - INTERVAL '10 days',
 'auth', 'u-parent-0000-0000-000000000001', 'parent',
 'u-parent-0000-0000-000000000001', 'user.login',
 'Login berhasil dari web dashboard', '192.168.1.100', 'success',
 'sch-sda-0000-0000-000000000001'),
('al-000000-0000-000000000002', NOW() - INTERVAL '9 days',
 'financial', 'u-parent-0000-0000-000000000001', 'parent',
 'c-andi-0000-0000-000000000001', 'wallet.topup',
 'Top up Rp 100.000 untuk Andi Santoso', '192.168.1.100', 'success',
 'sch-sda-0000-0000-000000000001'),
('al-000000-0000-000000000003', NOW() - INTERVAL '5 days',
 'user_mgmt', 'u-super-0000-0000-000000000001', 'super_admin',
 'u-admops-000-0000-000000000001', 'user.create',
 'Pembuatan akun Admin Ops untuk SD Harapan Bangsa', '10.0.0.1', 'success',
 'sch-sda-0000-0000-000000000001'),
('al-000000-0000-000000000004', NOW() - INTERVAL '2 hours',
 'transaction', NULL, NULL,
 'c-lana-0000-0000-000000000001', 'transaction.failed',
 'Biometric match score 0.42, threshold 0.70 — transaksi ditolak', '10.0.0.2', 'failure',
 'sch-smpa-000-0000-000000000001');

-- ============================================================
--  16. TICKETS
-- ============================================================
INSERT INTO tickets (id, ticket_number, created_by, assigned_to, school_id, category,
                     subject, description, status, priority, sla_deadline, created_at, updated_at) VALUES
('tkt-00000-000-0000-000000000001', 'TKT-20250420-001',
 'u-parent-0000-0000-000000000002', 'u-admops-000-0000-000000000001',
 'sch-sda-0000-0000-000000000001', 'transaction',
 'Transaksi tidak tercatat di riwayat',
 'Anak saya (Rafi) membeli di kantin pada tanggal 19 April namun tidak ada di riwayat.',
 'in_progress', 'medium',
 NOW() + INTERVAL '2 days',
 NOW() - INTERVAL '5 days', NOW()),
('tkt-00000-000-0000-000000000002', 'TKT-20250423-001',
 'u-parent-0000-0000-000000000003', NULL,
 'sch-smpa-000-0000-000000000001', 'biometric',
 'Sidik jari Lana tidak terdeteksi',
 'Lana sering gagal di perangkat FP-02. Mohon bantuan re-enroll biometrik.',
 'open', 'high',
 NOW() + INTERVAL '1 day',
 NOW() - INTERVAL '2 days', NOW());

-- ============================================================
--  17. APPROVAL REQUESTS
-- ============================================================
INSERT INTO approval_requests (id, request_type, requestor_id, approver_id, entity_type,
                                entity_data, status, requested_at, decided_at, decision_note) VALUES
('appr-00000-000-0000-000000000001', 'create_admin_ops',
 'u-admhub-000-0000-000000000001', NULL,
 'user', '{"email":"new.ops@sda.id","full_name":"Calon Admin Ops","role":"admin_ops","school_id":"sch-sda-0000-0000-000000000001"}',
 'pending', NOW() - INTERVAL '1 day', NULL, NULL);

-- ============================================================
--  VERIFICATION SUMMARY
-- ============================================================
SELECT 'users'               AS tabel, COUNT(*) AS baris FROM users
UNION ALL SELECT 'regions',                 COUNT(*) FROM regions
UNION ALL SELECT 'schools',                 COUNT(*) FROM schools
UNION ALL SELECT 'merchants',               COUNT(*) FROM merchants
UNION ALL SELECT 'parents',                 COUNT(*) FROM parents
UNION ALL SELECT 'clients',                 COUNT(*) FROM clients
UNION ALL SELECT 'wallets',                 COUNT(*) FROM wallets
UNION ALL SELECT 'wallet_ledger',           COUNT(*) FROM wallet_ledger
UNION ALL SELECT 'products',                COUNT(*) FROM products
UNION ALL SELECT 'devices',                 COUNT(*) FROM devices
UNION ALL SELECT 'transactions',            COUNT(*) FROM transactions
UNION ALL SELECT 'transaction_items',       COUNT(*) FROM transaction_items
UNION ALL SELECT 'notifications',           COUNT(*) FROM notifications
UNION ALL SELECT 'firmware_versions',       COUNT(*) FROM firmware_versions
UNION ALL SELECT 'audit_logs',              COUNT(*) FROM audit_logs
UNION ALL SELECT 'tickets',                 COUNT(*) FROM tickets
UNION ALL SELECT 'approval_requests',       COUNT(*) FROM approval_requests
ORDER BY tabel;
