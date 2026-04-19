# Product Requirements Document (PRD)
# Smart Access — Payment Transaction Platform (Biometric-Based)

---

## Document Information

| Field | Value |
|-------|-------|
| **Project Name** | Smart Access — Payment Transaction Platform |
| **Version** | 1.1 |
| **Date** | April 16, 2026 |
| **Previous Version** | PRD_SA v1.0 (Apr 15, 2026) |
| **Technology Stack** | Node.js (Backend) + Supabase (Database) |
| **Platform** | Web Dashboard (Admin) + Mobile App (Parent, Merchant, Admin) + Biometric Device (Client) |
| **Status** | Active Development |
| **Confidentiality** | Internal Use Only — PT KGiTON |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement](#2-problem-statement)
3. [Design Principles](#3-design-principles)
4. [Stakeholder Hierarchy & Roles](#4-stakeholder-hierarchy--roles)
5. [Permission Matrix](#5-permission-matrix)
6. [Ecosystem Architecture](#6-ecosystem-architecture)
7. [Core Business Model](#7-core-business-model)
8. [Operational Flow End-to-End](#8-operational-flow-end-to-end)
9. [Biometric System Specifications](#9-biometric-system-specifications)
10. [Transaction Lifecycle & Status Model](#10-transaction-lifecycle--status-model)
11. [Offline Mode & Sync](#11-offline-mode--sync)
12. [Notification System](#12-notification-system)
13. [Revenue Model & Cashflow](#13-revenue-model--cashflow)
14. [SLA & Escalation](#14-sla--escalation)
15. [Platform Strategy](#15-platform-strategy)
16. [Data Model](#16-data-model)
17. [System Architecture](#17-system-architecture)
18. [Dashboard & Monitoring](#18-dashboard--monitoring)
19. [Reporting & Analytics](#19-reporting--analytics)
20. [Exception Handling](#20-exception-handling)
21. [Security & Access Control](#21-security--access-control)
22. [Hardware & Infrastructure](#22-hardware--infrastructure)
23. [KPI & Success Metrics](#23-kpi--success-metrics)
24. [Non-Functional Requirements](#24-non-functional-requirements)
25. [Phasing & Roadmap](#25-phasing--roadmap)
26. [API Specifications](#26-api-specifications)
27. [Glossary](#27-glossary)

---

## 1. Executive Summary

### 1.1 Purpose

**Smart Access** adalah platform teknologi all-in-one yang menyediakan sistem pembayaran berbasis **dual-biometric** (Fingerprint + Face Recognition) untuk ekosistem Satuan Pendidikan. Platform ini menggantikan penggunaan uang cash dan kartu NFC dengan identitas biometrik siswa sebagai metode pembayaran, serta menyediakan dashboard terpadu untuk monitoring dan kontrol keuangan secara real-time.

Smart Access beroperasi sebagai **platform teknologi (technology provider)**, **bukan** sebagai penyelenggara pembayaran. Seluruh aliran dana di-escrow dan diproses oleh **Winpay** sebagai Payment Gateway berlisensi. Smart Access tidak menyimpan dana pengguna — seluruh saldo dikelola langsung oleh Winpay.

### 1.2 Background

Ekosistem pembayaran di satuan pendidikan Indonesia masih didominasi oleh penggunaan uang cash dan kartu NFC, yang menimbulkan berbagai masalah: kehilangan uang, ketidakmampuan orang tua untuk memonitor/mengontrol pengeluaran anak, risiko penyalahgunaan kartu NFC, serta tidak adanya data analytics untuk pengambilan keputusan.

Smart Access mengubah pendekatan dari **cash/card-based payment** menjadi **biometric-based payment** dimana setiap siswa memiliki identitas unik yang tidak bisa hilang, dipinjamkan, atau dipalsukan.

### 1.3 What Changed from v1.0

| Aspek | PRD v1.0 (Lama) | PRD v1.1 (Baru) |
|-------|-----------------|-----------------------------|
| Struktur Dokumen | 19 sections (compact) | 27 sections (comprehensive, aligned with LMS PRD standard) |
| Design Principles | Tidak eksplisit | Ditambahkan section dedicated |
| Permission Matrix | Embedded di Functional Requirements | Separated into dedicated section |
| Ecosystem Architecture | Embedded di Entity Relationship | Expanded into dedicated section |
| Exception Handling | Tidak ada | Ditambahkan section dedicated |
| API Specifications | Tidak ada | Ditambahkan section dedicated |
| KPI & Success Metrics | Embedded di Goals | Separated into dedicated section |
| Dashboard Detail | Embedded di Reporting | Separated into dedicated section |

### 1.4 Target Market

Satuan Pendidikan di Indonesia yang mencakup:
- Sekolah Dasar (SD/MI)
- Sekolah Menengah Pertama (SMP/MTs)
- Sekolah Menengah Atas/Kejuruan (SMA/SMK/MA)
- Pondok Pesantren / Boarding School
- Perguruan Tinggi

### 1.5 Key Benefits

- Eliminasi risiko kehilangan uang cash dan kartu NFC
- Dual-biometric authentication (Fingerprint + Face Recognition) sebagai 2FA bawaan
- Real-time monitoring & kontrol pengeluaran anak oleh orang tua
- Daily spending limit configurable per anak
- Real-time settlement untuk merchant (via Winpay)
- Dashboard analytics terpadu per role
- Offline mode capability untuk resiliensi operasional
- Audit trail lengkap untuk semua aktivitas

---

## 2. Problem Statement

### 2.1 Masalah Sebelum Smart Access

| No | Masalah | Dampak |
|----|---------|--------|
| 1 | Siswa sering kehilangan uang cash | Kerugian finansial langsung bagi siswa dan orang tua |
| 2 | Orang tua tidak bisa monitoring pengeluaran jajan anak | Tidak ada visibilitas → tidak ada kontrol |
| 3 | Orang tua tidak bisa mengontrol jumlah jajan anak | Uang jajan seminggu bisa habis dalam 1-2 hari |
| 4 | Siswa merantau sulit dikirim uang secara langsung | Orang tua harus bergantung pada pihak ketiga atau transfer manual |
| 5 | Kartu NFC rawan patah/rusak | Siswa harus beli kartu baru dengan biaya tambahan |
| 6 | Tidak ada 2FA pada NFC | Risiko penyalahgunaan jika kartu ditemukan orang lain |
| 7 | NFC dapat dipakai oleh siswa lain | Tidak ada verifikasi identitas pemegang kartu |
| 8 | Kehilangan NFC → biaya denda | Beban finansial tambahan bagi orang tua |

### 2.2 Why Biometric?

Biometrik menyelesaikan **semua** pain point di atas karena:
- **Tidak bisa hilang** — wajah dan sidik jari selalu melekat pada pemiliknya
- **Tidak bisa dipinjamkan** — identitas biometrik bersifat non-transferable
- **Dual-factor by design** — menggunakan Fingerprint + Face Recognition sebagai 2FA bawaan
- **Zero replacement cost** — tidak ada kartu fisik yang perlu diganti

### 2.3 Business Objectives

| ID | Objective | Success Metric |
|----|-----------|----------------|
| BO-01 | Mencegah kehilangan uang untuk siswa | 0% insiden kehilangan uang terkait metode pembayaran |
| BO-02 | Real-time monitoring pengeluaran anak | Notifikasi transaksi diterima < 5 detik setelah transaksi |
| BO-03 | Kontrol limit pengeluaran harian | 100% parent account memiliki fitur limit setting aktif |
| BO-04 | Eliminasi kebutuhan uang cash langsung | Top-up digital tersedia 24/7 via QRIS, Transfer, dan VA |
| BO-05 | Eliminasi kehilangan NFC atau uang cash | 0% insiden terkait kartu atau cash |
| BO-06 | Real-time settlement untuk merchant | Settlement time ≤ 5 detik setelah transaksi sukses |
| BO-07 | Data analytics untuk pengambilan keputusan | Dashboard analytics tersedia per role |
| BO-08 | Scalable dari satu sekolah hingga nasional | Arsitektur mendukung multi-tenant, multi-region |

---

## 3. Design Principles

### 3.1 Biometric-First Identity
Setiap client (siswa) memiliki identitas unik berbasis dual-biometric: **Fingerprint + Face Recognition**. Biometrik adalah primary authentication, PIN adalah fallback.

### 3.2 Event-Driven Transaction
Sistem mencatat **setiap event transaksi** dan perubahan saldo secara real-time, bukan hanya status terakhir. Audit log adalah sumber kebenaran utama.

### 3.3 Pisahkan Saldo, Limit, dan Status
- **Saldo (Balance)**: jumlah dana tersedia di Winpay untuk client
- **Daily Spending Limit**: batas pengeluaran harian yang diatur oleh parent
- **Account Status**: active, suspended, locked, pending_deletion

> Contoh: Client memiliki saldo Rp 100.000 tapi daily limit Rp 50.000 → maksimal transaksi hari itu Rp 50.000.

### 3.4 Exception-First Design
Sistem didesain untuk menangani kasus abnormal:
- Biometric gagal (FRR/FAR)
- Device offline, internet putus
- Overdraft saat offline sync
- Refund request, dispute transaksi
- Account lock, PIN failed

### 3.5 Real-time Settlement
Setiap transaksi di-settle secara real-time melalui Winpay. Saldo merchant langsung bertambah setelah transaksi sukses — tidak ada pending settlement.

### 3.6 Auditability
Setiap keputusan penting memiliki: siapa, kapan, dari device mana, terhadap client/merchant apa, dan perubahan sebelum/sesudah.

### 3.7 Minimal Manual Entry
Flow utama menggunakan biometric scan, automated settlement, push notification. Manual input hanya untuk exception handling (refund, override, enrollment).

---

## 4. Stakeholder Hierarchy & Roles

### 4.1 Role Hierarchy

```
                    ┌─────────────────────────┐
                    │       SUPER ADMIN       │
                    │    (Admin Nasional)     │
                    └────────────┬────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
    ┌─────────▼──────────┐      │     ┌────────────▼────────────┐
    │     ADMIN HUB      │    ...     │       ADMIN HUB        │
    │  (Regional Jabar)  │            │    (Regional Jatim)    │
    └─────────┬──────────┘            └────────────┬────────────┘
              │                                    │
    ┌─────────▼──────────┐           ┌─────────────▼────────────┐
    │   ADMIN OPERATIONS │           │     ADMIN OPERATIONS     │
    │   (Sekolah A)      │           │     (Sekolah B)          │
    └───┬──────┬─────────┘           └──────────────────────────┘
        │      │
   ┌────▼──┐ ┌▼──────────┐
   │MERCH- │ │  PARENTS   │
   │ANTS   │ │            │
   └───────┘ └──────┬─────┘
                    │ 1:N
             ┌──────▼─────┐
             │  CLIENTS   │
             │  (Siswa)   │
             └────────────┘
```

### 4.2 Detail Per-Role

#### SuperAdmin (Nasional)

| Aspek | Detail |
|-------|--------|
| **Scope** | Seluruh sistem nasional |
| **Dapat Membuat** | Admin Hub |
| **Approval** | Final approval pembuatan Admin Operations (dari Admin Hub) |
| **Monitoring** | Cashflow nasional, per-regional, per-cabang |
| **Akses** | Mengakses dan mengontrol semua Admin Hub |
| **Support** | Handle support masalah jika SLA Admin Hub terlewat (72-96 Jam) |
| **Tidak Dapat** | Membuat Admin Operations, Merchants, Users secara langsung |

#### Admin Hub (Regional)

| Aspek | Detail |
|-------|--------|
| **Scope** | 1 regional (contoh: Provinsi Jawa Barat) |
| **Dapat Membuat** | Admin Operations (butuh approval SuperAdmin) |
| **Monitoring** | Cashflow seluruh cabang di regionalnya |
| **Support** | Handle support masalah jika SLA Admin Ops terlewat (24-72 Jam) |
| **Tidak Dapat** | Membuat Merchants, Users/Parents/Clients secara langsung |
| **Tidak Dapat** | Mengakses regional lain |

#### Admin Operations (Cabang / Sekolah)

| Aspek | Detail |
|-------|--------|
| **Scope** | 1 Cabang / 1 Ekosistem Sekolah |
| **Dapat Membuat** | Merchants, Parents, Clients **tanpa perlu approval** |
| **Monitoring** | Cashflow cabang (transaksi, fee, settlement) |
| **Support** | First-line support, SLA < 24 Jam |
| **Biometric** | Melakukan enrollment biometrik siswa |
| **Approval** | Menyetujui atau menolak permintaan refund |
| **Bulk** | Import data siswa/client via CSV/batch upload |
| **Tidak Dapat** | Mengakses cabang lain (cashflow maupun teknis) |

#### Merchant (Pelaku Usaha)

| Aspek | Detail |
|-------|--------|
| **Scope** | Bisnis sendiri dalam 1 sekolah |
| **Jenis** | Kantin, Laundry, Minimarket, Fotokopi, dan usaha lainnya |
| **Platform** | Mobile App (Android/iOS) — optimized untuk POS |
| **Fungsi** | Mengelola produk, menerima pembayaran biometrik, melihat report penjualan |
| **Catatan** | 1 Merchant = 1 Sekolah. Jika pemilik sama punya usaha di sekolah lain → akun terpisah |
| **Tidak Dapat** | Mengakses data merchant lain, melihat saldo/data pribadi client/parent |

#### Parent / User (Orang Tua/Wali)

| Aspek | Detail |
|-------|--------|
| **Scope** | Akun sendiri dan anak/client yang terhubung |
| **Platform** | Mobile App (Android/iOS) |
| **Fungsi** | Top-up saldo, monitoring real-time, spending control, report pengeluaran |
| **Cardinality** | 1 Parent → Many Clients (One-to-Many) |
| **Catatan** | 1 akun Parent dapat digunakan bersama oleh ayah dan ibu (shared account) |

#### Client (Siswa)

| Aspek | Detail |
|-------|--------|
| **Scope** | Transaksi dan penggunaan pribadi |
| **Platform** | Biometric Device saja (tidak ada app) |
| **Fungsi** | Pembayaran biometrik di merchant, lihat saldo (via parent), riwayat transaksi |
| **Catatan** | Entity terpisah dari Parent. Terdaftar dalam sistem biometrik dan melakukan transaksi langsung di lapangan |

---

## 5. Permission Matrix

### 5.1 User & Entity Management

| Permission | SuperAdmin | Admin Hub | Admin Ops | Merchant | Parent | Client |
|-----------|:----------:|:---------:|:---------:|:--------:|:------:|:------:|
| Buat Admin Hub | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Buat Admin Ops | ✗ | ✓* | ✗ | ✗ | ✗ | ✗ |
| Approve Admin Ops | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Buat Merchant | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ |
| Buat Parent | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ |
| Buat Client | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ |
| Bulk Import (CSV) | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ |
| Hapus Admin Ops | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Hapus Admin Hub | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Request Account Deletion | ✗ | ✗ | ✓ | ✗ | ✓ | ✗ |

> `✓*` = Butuh approval dari level atas

### 5.2 Operational Permissions

| Permission | SuperAdmin | Admin Hub | Admin Ops | Merchant | Parent | Client |
|-----------|:----------:|:---------:|:---------:|:--------:|:------:|:------:|
| Enroll Biometric | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ |
| Re-enroll Biometric | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ |
| CRUD Produk | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ |
| Top Up Saldo | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ |
| Set Spending Limit | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ |
| Process Payment | ✗ | ✗ | ✗ | ✓ | ✗ | ✓ |
| Request Refund | ✗ | ✗ | ✗ | ✓ | ✓ | ✗ |
| Approve Refund | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ |
| Unlock Account | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ |
| Open Ticket | ✗ | ✗ | ✗ | ✓ | ✓ | ✗ |
| Manage Ticket | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ |

### 5.3 Monitoring & Reporting

| Permission | SuperAdmin | Admin Hub | Admin Ops | Merchant | Parent | Client |
|-----------|:----------:|:---------:|:---------:|:--------:|:------:|:------:|
| Cashflow Nasional | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Cashflow Regional | ✓ | ✓ (own) | ✗ | ✗ | ✗ | ✗ |
| Cashflow Cabang | ✓ | ✓ (own region) | ✓ (own) | ✗ | ✗ | ✗ |
| Report Penjualan | ✓ | ✓ | ✓ | ✓ (own) | ✗ | ✗ |
| Report Pengeluaran Anak | ✗ | ✗ | ✗ | ✗ | ✓ (own) | ✓ (own) |
| Dashboard | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ |
| Export Report | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ |
| View Audit Log | ✓ | ✓ (own region) | ✓ (own branch) | ✗ | ✗ | ✗ |

---

## 6. Ecosystem Architecture

### 6.1 Ecosystem Structure

```
┌──────────────────────────────────────────────────────────────────────┐
│                     SUPER ADMIN (Nasional)                           │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────────────────┐  ┌─────────────────────────────┐    │
│  │   ADMIN HUB (Regional A)    │  │  ADMIN HUB (Regional B)     │    │
│  ├─────────────────────────────┤  ├─────────────────────────────┤    │
│  │                             │  │                             │    │
│  │  ┌──── EKOSISTEM 1 ──────┐  │  │  ┌──── EKOSISTEM 3 ───────┐ │    │
│  │  │  Sekolah SDN 01       │  │  │  │  SMA Negeri 2          │ │    │
│  │  │  ├── Kantin Bu Sri    │  │  │  │  ├── Kantin Pak Joko   │ │    │
│  │  │  ├── Kantin Pak Adi   │  │  │  │  ├── Fotokopi Cepat    │ │    │
│  │  │  ├── Minimarket XYZ   │  │  │  │  └── Laundry Clean     │ │    │
│  │  │  ├── Parents (500)    │  │  │  │                        │ │    │
│  │  │  └── Clients (800)    │  │  │  └────────────────────────┘ │    │
│  │  └───────────────────────┘  │  │                             │    │
│  │                             │  └─────────────────────────────┘    │
│  │  ┌──── EKOSISTEM 2 ──────┐  │                                     │
│  │  │  SMP Boarding School  │  │                                     │
│  │  │  ├── Kantin Asrama    │  │                                     │
│  │  │  ├── Koperasi Sekolah │  │                                     │
│  │  │  ├── Parents (300)    │  │                                     │
│  │  │  └── Clients (400)    │  │                                     │
│  │  └───────────────────────┘  │                                     │
│  │                             │                                     │
│  └─────────────────────────────┘                                     │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

### 6.2 Ecosystem Rules

| Rule | Detail |
|------|--------|
| 1 SuperAdmin | Memonitor seluruh Admin Hub |
| 1 Admin Hub | Bisa punya **beberapa Admin Ops (Sekolah)** |
| 1 Admin Ops | Mengelola **1 sekolah** dengan merchants, parents, clients |
| Merchant → School | 1 Merchant **hanya** terdaftar di **1 sekolah** |
| Client → School | 1 Client **hanya** terdaftar di **1 sekolah** |
| Cross-School | **TIDAK bisa** transaksi antar sekolah |
| Pembuatan Admin Ops Baru | Admin Hub request → SuperAdmin approve |

### 6.3 Entity Cardinality

| Relationship | Cardinality | Keterangan |
|-------------|-------------|------------|
| SuperAdmin → Admin Hub | 1 : N | 1 SuperAdmin membawahi banyak Admin Hub |
| Admin Hub → Admin Ops | 1 : N | 1 Admin Hub membawahi banyak Admin Ops |
| Admin Ops → Merchant | 1 : N | 1 sekolah memiliki banyak merchant |
| Admin Ops → Parent | 1 : N | 1 sekolah memiliki banyak parent terdaftar |
| Admin Ops → Client | 1 : N | 1 sekolah memiliki banyak client/siswa |
| Parent → Client | 1 : N | 1 parent bisa memiliki banyak anak/client |
| Merchant → School | 1 : 1 | 1 merchant hanya terdaftar di 1 sekolah |
| Merchant → Product | 1 : N | 1 merchant memiliki banyak produk |
| Client → Transaction | 1 : N | 1 client memiliki banyak transaksi |

### 6.4 Core Entity Diagram

```
┌──────────────┐     1:N      ┌──────────────┐
│  SuperAdmin  │────────────▶│   Admin Hub   │
└──────────────┘              └──────┬───────┘
                                     │ 1:N
                                     ▼
                              ┌──────────────┐
                              │  Admin Ops   │
                              └──────┬───────┘
                                     │ 1:N           1:N
                              ┌──────┴──────┐────────────┐
                              ▼             ▼            ▼
                        ┌──────────┐  ┌──────────┐ ┌──────────┐
                        │ Merchant │  │  Parent  │ │  Client  │
                        └──────────┘  └────┬─────┘ └──────────┘
                                           │ 1:N        ▲
                                           └────────────┘
```

---

## 7. Core Business Model

### 7.1 Konsep Dasar

Smart Access adalah **biometric-first payment platform** dimana:
- **Client (siswa)** melakukan pembayaran menggunakan Fingerprint + Face Recognition
- **Parent** melakukan top-up saldo dan mengatur spending limit
- **Merchant** menerima pembayaran dengan settlement real-time
- **Winpay** mengelola seluruh aliran dana sebagai escrow/payment gateway

### 7.2 Key Value Proposition

| Stakeholder | Value |
|-------------|-------|
| **Parents** | Real-time monitoring & kontrol pengeluaran anak, tidak perlu berikan cash |
| **Client (Siswa)** | Tidak ada risiko kehilangan uang/kartu, pembayaran cepat & aman |
| **Merchants** | Settlement real-time, pencatatan otomatis, eliminasi cash handling |
| **Satuan Pendidikan** | Ekosistem cashless yang aman, data analytics, zero-cash risk |

### 7.3 Dual-Biometric Payment Flow (Summary)

```
┌─────────────────────────────────────────────────────────────────────┐
│                  DUAL-BIOMETRIC PAYMENT FLOW                        │
└─────────────────────────────────────────────────────────────────────┘

  Merchant input produk & qty
         │
         ▼
  Client scan Fingerprint di device
         │
    [Match?]
    ├── YES → Lanjut ke Face Recognition
    │          │
    │     [Match?]
    │     ├── YES → Cek Saldo & Daily Limit
    │     │          ├── OK → Transaksi SUKSES
    │     │          │        ├── Debit saldo client (Winpay)
    │     │          │        ├── Credit saldo merchant (Winpay)
    │     │          │        └── Push notif ke Parent
    │     │          ├── Saldo kurang → DITOLAK
    │     │          └── Limit exceeded → DITOLAK
    │     └── NO → Retry 3x → Fallback PIN
    └── NO → Retry 3x → Fallback PIN
```

### 7.4 Edge Cases

| Kasus | Handling |
|-------|----------|
| Biometric gagal terus (FRR tinggi) | Fallback PIN, re-enrollment, device calibration |
| Internet putus di sekolah | Offline mode (max 24 jam, max Rp 50K/trx) |
| Overdraft saat offline sync | Auto-suspend client, notif Admin Ops, parent diminta top-up |
| Anak kembar identik | Dual-biometric (fingerprint akan berbeda), PIN fallback |
| Perubahan fisik anak (pertumbuhan) | Re-enrollment per kuartal |
| Device rusak/hilang | Remote wipe, spare device policy |

---

## 8. Operational Flow End-to-End

### 8.1 User Registration & Enrollment

```
Admin Ops mendaftarkan user:

1. Admin Ops membuat akun Parent (nama, email, phone)
2. Parent menerima email/SMS dengan kredensial + link download app
3. Admin Ops membuat akun Client (nama, NIS/NISN, kelas, parent assignment)
4. Parent menerima notifikasi bahwa anak berhasil ditambahkan
5. Admin Ops melakukan biometric enrollment:
   a. Fingerprint — min 2 jari (primary + backup)
   b. Face Recognition — min 3 angle (frontal, left, right)
6. Consent form dari parent tercatat dalam sistem
7. Client status: Enrolled & Active → Siap bertransaksi
```

**Kontrol Wajib:**
- Semua enrollment memerlukan consent parent yang tercatat
- Kualitas biometric divalidasi (minimum quality score threshold)
- Template biometrik di-encrypt (AES-256) sebelum disimpan
- Template disimpan sebagai mathematical vector, **bukan** raw image

### 8.2 Top Up Flow (Parent → Client Saldo)

```
1. Parent buka app → Pilih anak (jika multi-child)
2. Input nominal top-up (min Rp 10.000, max Rp 1.000.000)
3. Pilih payment method: QRIS / Transfer Bank / Virtual Account
4. Redirect ke payment page (Winpay)
5. Parent melakukan pembayaran
6. Winpay callback → Saldo terupdate di sistem
7. Push notification ke Parent: "Top-up Rp XXX berhasil untuk [nama anak]"
```

### 8.3 Purchase Transaction Flow (Client di Merchant)

```
1. Merchant pilih produk yang dibeli oleh client (di POS/app merchant)
2. Total belanja ditampilkan
3. Client scan fingerprint di biometric device
4. Sistem match fingerprint template (on-device, ≤ 1 detik)
5. Client scan wajah di camera device
6. Sistem match face template (on-device, ≤ 1.5 detik)
7. Verify: Identity + Saldo + Daily Limit
8. Jika OK:
   a. Debit saldo client via Winpay
   b. Credit saldo merchant via Winpay
   c. Fee platform dipotong otomatis
   d. Transaksi SUKSES, receipt ditampilkan
   e. Push notification ke Parent (≤ 5 detik)
9. Jika GAGAL:
   a. Saldo kurang → Transaksi DITOLAK, notif ke Parent
   b. Daily limit exceeded → Transaksi DITOLAK, notif ke Parent
   c. Biometric gagal → Retry 3x → Fallback PIN
```

### 8.4 Fallback PIN Authentication

```
Trigger Conditions:
- Fingerprint gagal 3x berturut-turut
- Face recognition gagal 3x berturut-turut
- Biometric device malfunction

Flow:
1. Client memasukkan 6-digit PIN pada device
2. PIN di-set saat enrollment oleh Parent (bisa diubah kapan saja)
3. Max 3 percobaan PIN → akun di-lock sementara (15 menit)
4. Notifikasi ke Parent jika fallback PIN digunakan
5. Transaksi dengan fallback PIN ditandai khusus di log

Fallback Hierarchy:
  Fingerprint (3x retry) → Face Recognition (3x retry) → PIN (3x retry) → Account Locked
                                                                               ↓
                                                                      Manual override
                                                                      oleh Admin Ops
```

### 8.5 Refund / Pembatalan Transaksi

```
1. Merchant / Parent submit refund request
2. Admin Operations review request
3. Admin Ops approve / reject
4. (If approved) Winpay reverse transaction
5. Saldo client dikembalikan, saldo merchant dikurangi
6. Notifikasi ke Parent & Merchant
```

**Kontrol:**
- Refund hanya bisa dilakukan dalam **24 jam** setelah transaksi
- Full refund (100% nominal transaksi)
- Refund tercatat sebagai transaksi terpisah (type: refund) dengan reference ke transaksi asal

### 8.6 Account Deletion Flow

```
1. Request deletion (by Admin Ops or Parent)
2. Konfirmasi via OTP ke Parent
3. Grace period: 14 x 24 jam (akun di-suspend, tidak bisa transact)
4. Notifikasi ke Parent di H-3, H-1, dan H-Day
5. Saldo > 0? → Pencairan saldo ke rekening bank parent (via Winpay)
6. Data biometrik dihapus permanen (hard delete)
7. Data transaksi di-archive (retain 5 tahun untuk compliance)
8. Account status → Deleted
```

### 8.7 Complete Cycle Diagram

```
                    ┌───────────────────┐
                    │   ADMIN OPS       │
                    │   (Enrollment)    │
                    └─────────┬─────────┘
                              │ Create Parent + Client
                              │ + Biometric Enrollment
                              ▼
         ┌──────────┐    ┌──────────┐
         │  PARENT   │    │  CLIENT  │
         │  (App)    │    │  (Siswa) │
         └────┬──────┘    └────┬─────┘
              │                │
         Top-Up         Biometric Payment
         (via Winpay)         │
              │                │
              ▼                ▼
         ┌──────────┐    ┌──────────────┐
         │  WINPAY  │    │  BIOMETRIC   │
         │  (PG)    │◄───│  DEVICE      │
         └────┬─────┘    └──────────────┘
              │
         Settlement
         (Real-time)
              │
              ▼
         ┌──────────┐
         │ MERCHANT │
         │  (POS)   │
         └──────────┘
```

---

## 9. Biometric System Specifications

### 9.1 Dual-Biometric Authentication

| Spec | Detail |
|------|--------|
| **Primary Factor** | Fingerprint (sidik jari) |
| **Secondary Factor** | Face Recognition (pengenalan wajah) |
| **Sequence** | Fingerprint **→** Face Recognition (sequential, bukan parallel) |
| **Fallback** | 6-digit PIN |
| **Processing** | On-device matching (template matching dilakukan di device) |

### 9.2 Fingerprint Specifications

| Spec | Requirement |
|------|-------------|
| **Sensor Type** | Capacitive atau Optical (minimum 500 dpi) |
| **Template Format** | ISO/IEC 19794-2 (Fingerprint Minutiae Data) |
| **Matching Algorithm** | 1:N matching (identify) dengan threshold configurable |
| **False Acceptance Rate (FAR)** | ≤ 0.001% (1 in 100,000) |
| **False Rejection Rate (FRR)** | ≤ 1% |
| **Enrollment** | Minimum 2 jari (primary + backup) — rekomendasi: jempol kanan + telunjuk kanan |
| **Match Time** | ≤ 1 detik |
| **Anti-spoofing** | Liveness detection wajib (detect fake/silicone finger) |

### 9.3 Face Recognition Specifications

| Spec | Requirement |
|------|-------------|
| **Camera** | Minimum 2MP, IR-capable (untuk low-light) |
| **Template Format** | Vendor-specific face embedding vector (128/512-dimensional) |
| **Matching Algorithm** | 1:N matching dengan threshold configurable |
| **False Acceptance Rate (FAR)** | ≤ 0.01% (1 in 10,000) |
| **False Rejection Rate (FRR)** | ≤ 2% |
| **Enrollment** | Minimum 3 angle capture (frontal, slight-left, slight-right) |
| **Match Time** | ≤ 1.5 detik |
| **Anti-spoofing** | Liveness detection wajib (detect photo/video attack) |
| **Lighting** | Harus berfungsi di indoor lighting standar (200-500 lux) |

### 9.4 Biometric Data Security

| Aspect | Requirement |
|--------|-------------|
| **Storage** | Encrypted template only — **TIDAK** menyimpan raw image |
| **Encryption at Rest** | AES-256 |
| **Encryption in Transit** | TLS 1.3 |
| **Template Storage Location** | On-device (primary) + Server (backup, encrypted) |
| **Access Control** | Hanya biometric service yang bisa akses template store |
| **Deletion** | Hard delete — tidak ada soft delete untuk data biometrik |
| **Compliance** | UU PDP No. 27/2022 — Data Spesifik |

### 9.5 Re-enrollment Policy

| Aspek | Detail |
|-------|--------|
| **Jadwal** | Reminder setiap **3 bulan (per kuartal)** |
| **Pelaku** | Admin Ops |
| **Alasan** | Perubahan fisik anak (pertumbuhan), template degradation |
| **Mekanisme** | Re-enrollment tidak menghapus data lama sampai data baru terverifikasi |
| **Logging** | Log re-enrollment tercatat di audit trail |

---

## 10. Transaction Lifecycle & Status Model

### 10.1 Transaction Types

| No | Type | Kode | Deskripsi |
|---|---|---|---|
| 1 | Top Up | `TOPUP` | Parent mengisi saldo untuk client via Winpay |
| 2 | Purchase | `PURCHASE` | Client membeli produk di merchant via biometric |
| 3 | Refund | `REFUND` | Pengembalian dana karena pembatalan transaksi |
| 4 | Withdrawal | `WITHDRAWAL` | Pencairan saldo saat account deletion |

### 10.2 Transaction Status

| No | Status | Kode | Deskripsi |
|---|---|---|---|
| 1 | Pending | `PENDING` | Transaksi sedang diproses (menunggu Winpay) |
| 2 | Success | `SUCCESS` | Transaksi berhasil, saldo terupdate |
| 3 | Failed | `FAILED` | Transaksi gagal (saldo kurang, limit, error) |
| 4 | Refunded | `REFUNDED` | Transaksi telah di-refund |
| 5 | Expired | `EXPIRED` | Transaksi top-up expired (tidak dibayar dalam timeout) |

### 10.3 Status Transition Rules

```
PENDING ──────────► SUCCESS       (Winpay confirm payment)
PENDING ──────────► FAILED        (Winpay reject / error)
PENDING ──────────► EXPIRED       (Payment timeout)
SUCCESS ──────────► REFUNDED      (Approved refund within 24h)
```

### 10.4 Illegal Transitions (Sistem Harus Tolak)

- `FAILED` → `SUCCESS` (tanpa ulang proses)
- `EXPIRED` → `SUCCESS` (harus buat top-up baru)
- `REFUNDED` → `SUCCESS` (final state)
- `REFUNDED` → `REFUNDED` (tidak bisa double refund)

### 10.5 Account Status Model

| No | Status | Kode | Deskripsi |
|---|---|---|---|
| 1 | Active | `ACTIVE` | Akun aktif, bisa bertransaksi |
| 2 | Inactive | `INACTIVE` | Akun belum diaktifkan |
| 3 | Suspended | `SUSPENDED` | Akun di-suspend (pending deletion, overdraft) |
| 4 | Locked | `LOCKED` | Akun terkunci (3x PIN gagal) |
| 5 | Pending Deletion | `PENDING_DELETION` | Dalam grace period 14 hari |
| 6 | Deleted | `DELETED` | Akun dihapus permanen |

---

## 11. Offline Mode & Sync

### 11.1 Overview

Offline mode memungkinkan transaksi tetap berjalan saat koneksi internet terputus. Device menyimpan data secara lokal dan melakukan sinkronisasi saat koneksi kembali.

### 11.2 Offline Capabilities

| Capability | Status | Detail |
|------------|--------|--------|
| Biometric Matching | ✅ Offline | Template di-cache di device |
| Transaction Processing | ✅ Offline | Transaksi di-queue secara lokal |
| Balance Check | ⚠️ Limited | Menggunakan last-known balance dari cache |
| Top Up | ❌ Online only | Memerlukan Winpay connection |
| Notification | ❌ Online only | Push notif dikirim saat sync |
| Report & Analytics | ❌ Online only | Data hanya tersedia online |

### 11.3 Offline Transaction Rules

| Rule | Detail |
|------|--------|
| **Maximum offline duration** | **24 jam** — setelah itu device wajib online untuk sync |
| **Maximum offline transactions** | 200 transaksi per device |
| **Maximum amount per offline transaction** | Rp 50.000 |
| **Maximum total offline amount per client** | Rp 100.000 |
| **Balance validation** | Menggunakan last-synced balance (risk: potential overdraft) |
| **Daily limit validation** | Menggunakan local counter (risk: potential override jika client pakai device berbeda) |

### 11.4 Sync Mechanism

```
Device kembali online
       ↓
1. Upload queued transactions ke server (batch)
       ↓
2. Server validasi setiap transaksi:
   ├── Saldo cukup → Process & settle via Winpay
   ├── Saldo kurang → Flag as "overdraft" → notify Admin Ops
   └── Duplicate detected → Skip
       ↓
3. Download updated balance & biometric templates
       ↓
4. Clear local queue
       ↓
5. Send pending notifications ke Parents
```

### 11.5 Conflict Resolution

| Scenario | Resolution |
|----------|-----------:|
| **Overdraft** (saldo minus setelah sync) | Admin Ops notified → Parent diminta top-up → Akun client di-suspend sampai saldo positif |
| **Duplicate transaction** | System detect via idempotency key → skip duplicate |
| **Biometric template outdated** | Force re-download saat online |
| **Time discrepancy** | Gunakan device local time + server reconciliation saat sync |

---

## 12. Notification System

### 12.1 Notification Types

| Event | Recipient | Channel | Timing |
|-------|-----------|---------|--------|
| **Transaksi berhasil** | Parent | Push Notif + In-app | Real-time (≤ 5 detik) |
| **Transaksi gagal** | Parent | Push Notif + In-app | Real-time |
| **Top-up berhasil** | Parent | Push Notif + In-app | Real-time |
| **Daily limit 80% reached** | Parent | Push Notif | Real-time |
| **Daily limit exceeded (transaksi ditolak)** | Parent | Push Notif | Real-time |
| **Fallback PIN digunakan** | Parent | Push Notif | Real-time |
| **Akun terkunci (3x PIN gagal)** | Parent + Admin Ops | Push Notif | Real-time |
| **Biometric re-enrollment reminder** | Parent + Admin Ops | Push Notif + Email | 7 hari sebelum deadline |
| **Ticket update** | Requester | Push Notif + In-app | Real-time |
| **Approval request** | SuperAdmin | Push Notif + Email | Real-time |
| **SLA breach warning** | Admin Hub / SuperAdmin | Push Notif + Email | Real-time |
| **Account deletion countdown** | Parent | Push Notif | H-3, H-1, H-Day |
| **Settlement received** | Merchant | Push Notif + In-app | Real-time |
| **Low saldo alert** | Parent | Push Notif | Saat saldo < threshold |

### 12.2 Notification Format — Transaksi Berhasil

```
📱 Push Notification:

Smart Access — Transaksi Berhasil ✅

[Nama Anak] baru saja melakukan pembelian:
🏪 Merchant: Kantin Bu Sri
🍽️ Produk: Nasi Goreng, Es Teh
💰 Total: Rp 18.000
💳 Sisa Saldo: Rp 82.000
📊 Limit Hari Ini: Rp 18.000 / Rp 50.000

📅 15 Apr 2026, 12:15 WIB
```

### 12.3 Push Notification Infrastructure

| Platform | Service |
|----------|---------|
| **Android** | Firebase Cloud Messaging (FCM) |
| **iOS** | Apple Push Notification Service (APNs) |
| **Fallback** | SMS notification untuk critical events (akun terkunci, large transactions) |

---

## 13. Revenue Model & Cashflow

### 13.1 Revenue Streams

| # | Stream | Payer | Model | Keterangan |
|---|--------|-------|-------|------------|
| 1 | **Top-up Fee** | Parent | Per-transaksi | Fee dikenakan setiap kali parent melakukan top-up saldo |
| 2 | **Transaction Fee** | Client (dari pengeluaran) | Per-transaksi | Fee dikenakan dari setiap pembelian yang dilakukan client |
| 3 | **Device Subscription** | Merchant | Bulanan | Merchant menyewa biometric device secara bulanan |
| 4 | **Device Purchase** | Merchant | One-time | Merchant membeli biometric device secara putus |
| 5 | **Platform Subscription** | Admin Ops (Sekolah) | Bulanan | Sekolah membayar subscription untuk menggunakan platform |

### 13.2 Fee Structure (To Be Defined)

> **Catatan:** Angka persentase dan nominal fee di bawah ini adalah **placeholder** dan harus dikonfirmasi oleh tim bisnis.

| Revenue Stream | Placeholder Rate | Catatan |
|----------------|-----------------|---------| 
| Top-up Fee | Rp 1.000 - 2.500 per top-up | Flat fee per transaksi top-up |
| Transaction Fee | 1% - 2.5% per transaksi | Persentase dari nilai transaksi pembelian |
| Device Subscription | Rp 150.000 - 300.000/bulan | Per device per bulan |
| Device Purchase | Rp 2.000.000 - 5.000.000 | One-time per device |
| Platform Subscription | Rp 500.000 - 2.000.000/bulan | Per sekolah per bulan, tier berdasarkan jumlah siswa |

### 13.3 PG Fee Handling

| Item | Detail |
|------|--------|
| **Payment Gateway Fee** | Ditanggung oleh **Platform (Smart Access)** |
| **Implication** | Fee PG Winpay menjadi cost of goods sold platform |
| **Perlu dihitung** | Margin analysis: revenue per transaksi vs PG cost per transaksi |

### 13.4 Settlement Flow

| Step | Proses | Timing |
|------|--------|--------|
| 1 | Client bayar di merchant | T+0 |
| 2 | Winpay debit saldo client | T+0 (real-time) |
| 3 | Winpay credit saldo merchant | T+0 (real-time) |
| 4 | Fee platform dipotong otomatis | T+0 (real-time) |
| 5 | Merchant dapat melihat saldo terupdate | T+0 (real-time) |

> Settlement bersifat **real-time** — saldo merchant langsung bertambah setelah transaksi sukses.

### 13.5 Fee & Deduction Example

```
Contoh: Client beli Nasi Goreng Rp 15.000

Parent saldo (Winpay): Rp 100.000
├── Debit: Rp 15.000 (harga produk)
├── Debit: Rp XXX (fee transaksi platform — dari sisi client/parent)
└── Remaining: Rp 100.000 - 15.000 - fee

Merchant saldo (Winpay):
├── Credit: Rp 15.000 (harga produk)
└── Debit: Rp XXX (MDR/fee — jika ada, dari sisi merchant)

Platform revenue:
├── Fee top-up (dari parent saat top-up)
├── Fee transaksi (dari pengeluaran client)
├── Subscription device (dari merchant, bulanan)
└── Subscription platform (dari Admin Ops, bulanan)
```

### 13.6 Cashflow Hierarchy

```
┌──────────────────────────────────────────┐
│  SUPER ADMIN — Cashflow Nasional         │
│  Melihat total revenue, cost, profit     │
│  dari semua regional dan cabang          │
├──────────────────────────────────────────┤
│                                          │
│  ┌──────────────────────────────────┐    │
│  │ ADMIN HUB — Cashflow Regional    │    │
│  │ Total semua sekolah di regional  │    │
│  ├──────────────────────────────────┤    │
│  │                                  │    │
│  │  ┌─────────────────────────┐     │    │
│  │  │ ADMIN OPS — Cashflow    │     │    │
│  │  │ Cabang                  │     │    │
│  │  │ Revenue: Fee topup      │     │    │
│  │  │ + Fee transaksi         │     │    │
│  │  │ + Subscription          │     │    │
│  │  ├─────────────────────────┤     │    │
│  │  │                         │     │    │
│  │  │ MERCHANT — Penjualan    │     │    │
│  │  │ PARENT — Pengeluaran    │     │    │
│  │  │ (monitoring saja)       │     │    │
│  │  └─────────────────────────┘     │    │
│  └──────────────────────────────────┘    │
└──────────────────────────────────────────┘
```

---

## 14. SLA & Escalation

### 14.1 Problem Resolution SLA

| Level | SLA | Trigger Escalation |
|-------|-----|-------------------|
| **Admin Operations** | 0–24 Jam | First-line support, handle langsung |
| **Admin Hub** | 24–72 Jam | Jika masalah tidak ditangani oleh Admin Ops |
| **SuperAdmin** | 72–96 Jam | Jika masalah tidak ditangani oleh Admin Hub |

### 14.2 Escalation Mechanism (V1)

| Aspek | Detail |
|-------|--------|
| **Method** | Notifikasi-based |
| **Channel** | In-app notification + (optional) email/push notification |
| **Auto-assign** | Belum ada di V1 (hanya notifikasi ke level atas) |
| **Tracking** | Setiap escalation tercatat: waktu, dari siapa, ke siapa, masalah apa |

> **V2 Enhancement**: Auto-assign problem ke level atas jika SLA terlewat.

### 14.3 Support Ticketing Flow

```
User (Merchant/Parent) submit ticket via app
       ↓
Ticket masuk ke Admin Operations
       ↓
Admin Ops review & respond (SLA < 24 jam)
       ↓
   [Resolved?]
   ├── YES → Ticket closed, satisfaction survey
   └── NO → Escalate
              ├── SLA 24-72 jam → Escalate ke Admin Hub
              └── SLA 72-96 jam → Escalate ke SuperAdmin
```

### 14.4 SLA Matrix

| Level | Handled By | SLA Response | SLA Resolution |
|-------|-----------|-------------|---------------|
| Level 1 | Admin Operations | 2 jam | < 24 jam |
| Level 2 | Admin Hub | 4 jam | 24-72 jam |
| Level 3 | SuperAdmin | 8 jam | 72-96 jam |

### 14.5 Ticket Structure

| Field | Detail |
|-------|--------|
| **Ticket Number** | Auto-generated (format: TKT-YYYYMMDD-XXXX) |
| **Kategori** | Transaksi, Biometric, Akun, Lainnya |
| **Priority** | Low, Medium, High, Critical |
| **Attachment** | Foto, screenshot |
| **Status** | Open → In Progress → Resolved → Closed |

---

## 15. Platform Strategy

### 15.1 Platform Assignment per Role

| Role | Mobile App (iOS/Android) | Web Dashboard | Biometric Device | Keterangan |
|------|:------------------------:|:-------------:|:----------------:|------------|
| SuperAdmin | ✅ | ✅ | ✗ | Full access di kedua platform |
| Admin Hub | ✅ | ✅ | ✗ | Full access di kedua platform |
| Admin Operations | ✅ | ✅ | ✗ | Full access di kedua platform |
| Merchant | ✅ | ❌ | ✗ | Mobile-only, optimized untuk POS |
| Parent | ✅ | ❌ | ✗ | Mobile-only, real-time notification |
| Client | ❌ | ❌ | ✅ | Interaksi via biometric device saja |

### 15.2 Feature Distribution

| Feature | Mobile App | Web Dashboard | Biometric Device |
|---------|:----------:|:-------------:|:----------------:|
| Transaction Processing | ✅ (merchant) | ❌ | ✅ (client) |
| Real-time Notification | ✅ | ✅ | ❌ |
| Report & Analytics | ✅ (simplified) | ✅ (full) | ❌ |
| User Management | ✅ (basic) | ✅ (full + bulk) | ❌ |
| Biometric Enrollment | ❌ | ❌ | ✅ (via device) |
| Product Management | ✅ (merchant) | ❌ | ❌ |
| Ticket Management | ✅ | ✅ | ❌ |
| Bulk Import (CSV) | ❌ | ✅ | ❌ |
| System Configuration | ❌ | ✅ | ❌ |
| Top Up Saldo | ✅ (parent) | ❌ | ❌ |
| Spending Limit | ✅ (parent) | ❌ | ❌ |

### 15.3 Web Dashboard

| Aspek | Detail |
|-------|--------|
| **Target User** | Admin semua level (SuperAdmin, Admin Hub, Admin Ops) |
| **Technology** | Next.js + React (Web-based Dashboard) |
| **Fitur Utama** | Dashboard, CRUD entities, reporting, analytics, approval workflow, cashflow |
| **Browser** | Chrome, Edge, Firefox, Safari (latest) |

### 15.4 Mobile Application

| Aspek | Detail |
|-------|--------|
| **Target User** | Admin Ops, Merchant, Parent |
| **Technology** | Flutter / React Native |
| **Platform** | Android (8.0+) + iOS (14+) |
| **Fitur Utama** | POS (merchant), top-up & monitoring (parent), management (admin ops) |

---

## 16. Data Model

### 16.1 Core Entities

#### Organization Hierarchy

```
super_admin_config
  └── regions
       └── schools
            ├── merchants
            ├── parents
            └── clients
```

#### Regions (Admin Hub)

| Field | Type | Deskripsi |
|-------|------|-----------|
| `region_id` | UUID | Primary key |
| `region_code` | VARCHAR | Kode unik regional |
| `region_name` | VARCHAR | Nama regional (e.g., "Jawa Barat") |
| `province` | VARCHAR | Provinsi |
| `admin_user_id` | UUID | FK ke users |
| `status` | ENUM | ACTIVE / SUSPENDED |
| `created_by` | UUID | SuperAdmin yang membuat |
| `created_at` | TIMESTAMP | |

#### Schools (Admin Ops)

| Field | Type | Deskripsi |
|-------|------|-----------|
| `school_id` | UUID | Primary key |
| `region_id` | UUID | FK ke regions |
| `school_code` | VARCHAR | Kode sekolah |
| `school_name` | VARCHAR | Nama sekolah |
| `address` | TEXT | Alamat |
| `city` | VARCHAR | Kota |
| `admin_user_id` | UUID | FK ke users |
| `school_type` | ENUM | SD / SMP / SMA / SMK / BOARDING / UNIVERSITY |
| `status` | ENUM | ACTIVE / PENDING_APPROVAL / SUSPENDED |
| `approved_by` | UUID | SuperAdmin yang approve |

### 16.2 User Management

#### Users

| Field | Type | Deskripsi |
|-------|------|-----------|
| `user_id` | UUID | Primary key |
| `email` | VARCHAR | Email unik |
| `phone` | VARCHAR | Nomor HP |
| `password_hash` | VARCHAR | Password hash (bcrypt) |
| `full_name` | VARCHAR | Nama lengkap |
| `role_type` | ENUM | SUPERADMIN / ADMIN_HUB / ADMIN_OPS / MERCHANT / PARENT / CLIENT |
| `status` | ENUM | ACTIVE / INACTIVE / SUSPENDED / PENDING_DELETION |
| `created_at` | TIMESTAMP | |
| `updated_at` | TIMESTAMP | |
| `deleted_at` | TIMESTAMP | Soft delete |

#### Superadmins

| Field | Type | Deskripsi |
|-------|------|-----------|
| `id` | UUID | Primary key |
| `user_id` | UUID | FK → users |
| `name` | VARCHAR | |
| `scope` | VARCHAR | national |

#### Admin Hubs

| Field | Type | Deskripsi |
|-------|------|-----------|
| `id` | UUID | Primary key |
| `user_id` | UUID | FK → users |
| `name` | VARCHAR | |
| `region_id` | UUID | FK → regions |
| `created_by` | UUID | FK → superadmins |

#### Admin Ops

| Field | Type | Deskripsi |
|-------|------|-----------|
| `id` | UUID | Primary key |
| `user_id` | UUID | FK → users |
| `name` | VARCHAR | |
| `school_id` | UUID | FK → schools |
| `created_by` | UUID | FK → admin_hubs |
| `approved_by` | UUID | FK → superadmins |

### 16.3 Merchant & Product

#### Merchants

| Field | Type | Deskripsi |
|-------|------|-----------|
| `merchant_id` | UUID | Primary key |
| `user_id` | UUID | FK → users |
| `school_id` | UUID | FK → schools |
| `business_name` | VARCHAR | Nama bisnis |
| `business_type` | ENUM | KANTIN / LAUNDRY / MINIMARKET / FOTOKOPI / OTHER |
| `owner_name` | VARCHAR | Nama pemilik |
| `balance` | DECIMAL | Referenced from Winpay |
| `status` | ENUM | ACTIVE / SUSPENDED |

#### Products

| Field | Type | Deskripsi |
|-------|------|-----------|
| `product_id` | UUID | Primary key |
| `merchant_id` | UUID | FK → merchants |
| `name` | VARCHAR | Nama produk |
| `description` | TEXT | Deskripsi |
| `price` | DECIMAL | Harga (min Rp 500) |
| `category` | ENUM | MAKANAN / MINUMAN / SNACK / JASA / LAINNYA |
| `image_url` | VARCHAR | URL foto produk |
| `is_available` | BOOLEAN | Tersedia / tidak |
| `stock_quantity` | INT | Stok (nullable, optional feature) |

### 16.4 Parent & Client

#### Parents

| Field | Type | Deskripsi |
|-------|------|-----------|
| `parent_id` | UUID | Primary key |
| `user_id` | UUID | FK → users |
| `name` | VARCHAR | |
| `phone` | VARCHAR | |
| `school_id` | UUID | FK → schools |
| `daily_limit_default` | DECIMAL | Default limit untuk semua anak |

#### Clients

| Field | Type | Deskripsi |
|-------|------|-----------|
| `client_id` | UUID | Primary key |
| `user_id` | UUID | FK → users |
| `parent_id` | UUID | FK → parents |
| `school_id` | UUID | FK → schools |
| `name` | VARCHAR | |
| `student_id_number` | VARCHAR | NIS/NISN |
| `class` | VARCHAR | Kelas |
| `grade` | VARCHAR | Tingkat |
| `daily_spending_limit` | DECIMAL | Override dari parent |
| `biometric_enrolled` | BOOLEAN | Sudah enrollment? |
| `biometric_last_updated` | TIMESTAMP | |
| `balance` | DECIMAL | Referenced from Winpay |
| `pin_hash` | VARCHAR | Fallback PIN (6-digit, hashed) |
| `status` | ENUM | ACTIVE / SUSPENDED / LOCKED / PENDING_DELETION |

#### Biometric Records

| Field | Type | Deskripsi |
|-------|------|-----------|
| `biometric_id` | UUID | Primary key |
| `client_id` | UUID | FK → clients |
| `fingerprint_template` | BINARY | Encrypted binary template |
| `face_template` | BINARY | Encrypted binary template |
| `enrolled_at` | TIMESTAMP | |
| `last_updated_at` | TIMESTAMP | |
| `enrolled_by` | UUID | FK → admin_ops |
| `device_id` | UUID | FK → devices |

### 16.5 Transactions

#### Transactions

| Field | Type | Deskripsi |
|-------|------|-----------|
| `transaction_id` | UUID | Primary key |
| `transaction_ref` | VARCHAR | Unique, from Winpay |
| `type` | ENUM | TOPUP / PURCHASE / REFUND / WITHDRAWAL |
| `client_id` | UUID | FK → clients |
| `merchant_id` | UUID | FK → merchants (nullable) |
| `parent_id` | UUID | FK → parents (nullable, for topup) |
| `amount` | DECIMAL | Nominal transaksi |
| `fee_amount` | DECIMAL | Fee yang dikenakan |
| `status` | ENUM | PENDING / SUCCESS / FAILED / REFUNDED / EXPIRED |
| `payment_method` | ENUM | QRIS / BANK_TRANSFER / VA |
| `biometric_method` | ENUM | FINGERPRINT_FACE / FALLBACK_PIN |
| `offline_flag` | BOOLEAN | Transaksi offline? |
| `synced_at` | TIMESTAMP | Nullable, for offline transactions |
| `created_at` | TIMESTAMP | |
| `metadata` | JSONB | Product details, etc. |

#### Transaction Items

| Field | Type | Deskripsi |
|-------|------|-----------|
| `item_id` | UUID | Primary key |
| `transaction_id` | UUID | FK → transactions |
| `product_id` | UUID | FK → products |
| `product_name` | VARCHAR | Snapshot nama produk |
| `quantity` | INT | |
| `unit_price` | DECIMAL | |
| `subtotal` | DECIMAL | |

### 16.6 Support

#### Tickets

| Field | Type | Deskripsi |
|-------|------|-----------|
| `ticket_id` | UUID | Primary key |
| `ticket_number` | VARCHAR | Unique, auto-generated (TKT-YYYYMMDD-XXXX) |
| `created_by` | UUID | FK → users |
| `assigned_to` | UUID | FK → admin_ops |
| `category` | ENUM | TRANSACTION / BIOMETRIC / ACCOUNT / OTHER |
| `subject` | VARCHAR | |
| `description` | TEXT | |
| `status` | ENUM | OPEN / IN_PROGRESS / RESOLVED / CLOSED |
| `priority` | ENUM | LOW / MEDIUM / HIGH / CRITICAL |
| `sla_deadline` | TIMESTAMP | |
| `resolved_at` | TIMESTAMP | |
| `created_at` | TIMESTAMP | |

### 16.7 Notification & Audit

#### Notifications

| Field | Type | Deskripsi |
|-------|------|-----------|
| `notification_id` | UUID | Primary key |
| `recipient_user_id` | UUID | FK → users |
| `notification_type` | ENUM | TRANSACTION / TOPUP / LIMIT_ALERT / ACCOUNT_LOCK / APPROVAL / SLA_BREACH / SYSTEM |
| `title` | VARCHAR | |
| `message` | TEXT | |
| `reference_type` | VARCHAR | Entity yang direferensikan |
| `reference_id` | UUID | |
| `is_read` | BOOLEAN | |
| `created_at` | TIMESTAMP | |

#### Audit Log

| Field | Type | Deskripsi |
|-------|------|-----------|
| `log_id` | UUID | Primary key |
| `timestamp` | TIMESTAMP | ISO 8601 |
| `event_type` | VARCHAR | AUTH / USER_MGMT / BIOMETRIC / TRANSACTION / FINANCIAL / SYSTEM / SUPPORT |
| `actor_id` | UUID | FK → users |
| `actor_role` | VARCHAR | |
| `target_id` | UUID | Nullable |
| `action` | VARCHAR | |
| `details` | JSONB | |
| `ip_address` | VARCHAR | |
| `device_info` | VARCHAR | |
| `result` | ENUM | SUCCESS / FAILURE |
| `school_id` | UUID | FK → schools |

### 16.8 Approval Queue

#### Approval Request

| Field | Type | Deskripsi |
|-------|------|-----------|
| `approval_id` | UUID | Primary key |
| `request_type` | ENUM | CREATE_ADMIN_OPS / DELETE_ADMIN_OPS / REFUND |
| `requestor_id` | UUID | FK → users |
| `approver_id` | UUID | FK → users |
| `entity_type` | VARCHAR | |
| `entity_data` | JSONB | Data entity yang di-request |
| `status` | ENUM | PENDING / APPROVED / REJECTED |
| `requested_at` | TIMESTAMP | |
| `decided_at` | TIMESTAMP | |
| `decision_note` | TEXT | |

### 16.9 Devices

#### Biometric Devices

| Field | Type | Deskripsi |
|-------|------|-----------|
| `device_id` | UUID | Primary key |
| `device_serial` | VARCHAR | Serial number |
| `school_id` | UUID | FK → schools |
| `merchant_id` | UUID | FK → merchants (nullable) |
| `device_type` | ENUM | FINGERPRINT_READER / FACE_CAMERA / COMBO_DEVICE |
| `status` | ENUM | ACTIVE / OFFLINE / MAINTENANCE / RETIRED |
| `last_heartbeat` | TIMESTAMP | |
| `firmware_version` | VARCHAR | |
| `sdk_version` | VARCHAR | |

---

## 17. System Architecture

### 17.1 High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                SMART ACCESS — SYSTEM ARCHITECTURE                        │
└──────────────────────────────────────────────────────────────────────────┘

     ┌──────────────┐       ┌──────────────┐       ┌──────────────┐
     │     Web      │       │  Mobile App  │       │  Biometric   │
     │  Dashboard   │       │  (Parent,    │       │   Device     │
     │ (React/Next) │       │  Merchant,   │       │  (Embedded)  │
     │              │       │  Admin)      │       │              │
     └──────┬───────┘       └──────┬───────┘       └──────┬───────┘
            │                      │                      │
            └──────────────────────┼──────────────────────┘
                                   │
                       ┌───────────▼───────────┐
                       │     API Gateway       │
                       │   (Rate Limiting,     │
                       │    CORS, Auth)        │
                       └───────────┬───────────┘
                                   │
           ┌───────────────────────┼───────────────────────┐
           │                       │                       │
   ┌───────▼───────┐       ┌──────▼───────┐       ┌───────▼───────┐
   │   Auth API    │       │ Business API │       │  Report API   │
   │  (Auth &      │       │ (Transaction,│       │  (Analytics,  │
   │  User Mgmt)   │       │  Biometric,  │       │  Dashboard)   │
   │               │       │  Product)    │       │               │
   └───────┬───────┘       └──────┬───────┘       └───────┬───────┘
           │                      │                       │
           └──────────────────────┼───────────────────────┘
                                  │
                      ┌───────────▼───────────┐
                      │    SUPABASE CLOUD     │
                      ├───────────────────────┤
                      │  PostgreSQL Database  │
                      │  Supabase Auth        │
                      │  Supabase Storage     │
                      │  Supabase Realtime    │
                      │  Edge Functions       │
                      │  (Cron Jobs, etc)     │
                      └───────────┬───────────┘
                                  │
                      ┌───────────▼───────────┐
                      │   EXTERNAL SERVICES   │
                      ├───────────────────────┤
                      │  Winpay (Payment GW)  │
                      │  FCM / APNs (Push)    │
                      │  Biometric HW SDK     │
                      └───────────────────────┘
```

### 17.2 Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------| 
| **Web Dashboard** | Next.js + React | Admin panel, reporting, analytics |
| **Mobile App** | Flutter / React Native | Parent, Merchant, Admin Ops mobile experience |
| **Biometric Device** | Embedded Android | Fingerprint + Face recognition, POS |
| **API Server** | Node.js + Express/Fastify | RESTful API + WebSocket |
| **Authentication** | Supabase Auth + JWT | User auth + RBAC |
| **Database** | Supabase (PostgreSQL) | Primary data store |
| **File Storage** | Supabase Storage | Product images, ticket attachments |
| **Real-time** | Supabase Realtime | Live dashboard updates, notifications |
| **Background Jobs** | Supabase Edge Functions | SLA checker, scheduled reports, reconciliation |
| **Caching** | Redis (optional) | Performance optimization |
| **Payment Gateway** | Winpay | Top-up, debit, credit, refund, balance |

### 17.3 Key Architecture Decisions

| Decision | Rationale |
|----------|-----------| 
| **Microservice-ready Monolith** | Start as modular monolith, decompose ke microservices saat scale |
| **Event-driven untuk transaksi** | Real-time notification memerlukan event bus (WebSocket/SSE) |
| **Biometric processing on-device** | Template matching dilakukan di device — mengurangi latency dan risiko data leak |
| **Winpay sebagai source of truth untuk saldo** | Platform tidak menyimpan dana — query balance dari Winpay API |
| **Audit log append-only** | Compliance requirement — semua aktivitas tercatat dan tidak bisa di-modify |

### 17.4 Background Jobs (Scheduled)

| Job | Schedule | Fungsi |
|-----|----------|--------|
| `sla_breach_checker` | Every 1 hour | Cek SLA yang terlewat, kirim notifikasi |
| `daily_report_generator` | Daily 06:00 | Generate daily summary report |
| `biometric_re_enrollment_reminder` | Weekly | Cek enrollment > 3 bulan, kirim reminder |
| `daily_reconciliation` | Nightly 01:00 | Reconcile Smart Access ledger vs Winpay |
| `offline_sync_monitor` | Every 30 min | Cek device yang offline > 24 jam |

---

## 18. Dashboard & Monitoring

### 18.1 SuperAdmin Dashboard

| Widget | Deskripsi |
|--------|-----------|
| Total Transaksi Nasional | Volume & value transaksi nasional |
| Total Pengguna Aktif | Per region breakdown |
| Revenue Platform | Fee topup + fee transaksi + subscription |
| Top-performing Regions | Compare antar regional |
| Growth Metrics | MoM, YoY trends |
| SLA Compliance | % SLA terpenuhi per Admin Hub |
| Pending Approvals | Approval queue (create Admin Ops, dll) |
| System Health & Uptime | Server status, device online rate |

### 18.2 Admin Hub Dashboard

| Widget | Deskripsi |
|--------|-----------|
| Total Transaksi Regional | Volume & value regional |
| Total Pengguna Aktif | Per branch/sekolah |
| Revenue Regional | Total revenue regional |
| Top-performing Branches | Compare antar sekolah |
| SLA Compliance | Per Admin Ops |
| Growth Metrics Regional | Trend regional |
| Escalated Issues | Masalah yang di-eskalasi dari Admin Ops |

### 18.3 Admin Ops Dashboard

| Widget | Deskripsi |
|--------|-----------|
| Total Transaksi Cabang | Volume & value cabang |
| Total Merchant, Parent, Client Aktif | User counts |
| Revenue Cabang | Fee breakdown |
| Top-selling Products | Best products |
| Top Merchant by Revenue | Top earners |
| Average Transaction Value | Rata-rata transaksi |
| Biometric Enrollment Rate | % siswa ter-enroll |
| Support Ticket Summary | Open/resolved tickets |
| Daily/Weekly/Monthly Trends | Transaction trends |

### 18.4 Merchant Dashboard

| Widget | Deskripsi |
|--------|-----------|
| Total Penjualan | Daily, weekly, monthly |
| Revenue & Balance | Saldo merchant |
| Top-selling Products | Produk terlaris |
| Transaction Count per Product | Volume per produk |
| Average Transaction Value | Rata-rata per transaksi |
| Peak Hours Analysis | Jam sibuk |

### 18.5 Parent Dashboard

| Widget | Deskripsi |
|--------|-----------|
| Saldo Anak | Per child balance |
| Total Pengeluaran Hari Ini vs Limit | Limit usage |
| Riwayat Transaksi per Anak | Detail transactions |
| Riwayat Top-up | Top-up history |
| Spending Trends | Daily, weekly, monthly trends |
| Most Visited Merchants | Merchant favorites |
| Most Purchased Products | Product favorites |

---

## 19. Reporting & Analytics

### 19.1 Transaction Reports

| Report | Deskripsi | Access Level |
|--------|-----------|-------------|
| Transaction History | Daftar semua transaksi per periode | Admin Ops+ |
| Top-up History | Daftar top-up per parent/client | Admin Ops+, Parent |
| Refund Report | Daftar refund dan statusnya | Admin Ops+ |
| Failed Transaction Report | Transaksi gagal & alasan | Admin Ops+ |
| Offline Transaction Report | Transaksi offline & sync status | Admin Ops+ |
| Settlement Report | Settlement ke merchant per periode | Admin Ops+ |

### 19.2 User Reports

| Report | Deskripsi | Access Level |
|--------|-----------|-------------|
| User Enrollment Report | Status biometric enrollment | Admin Ops+ |
| Active Users Report | User aktif per periode | Admin Hub+, Admin Ops |
| Account Deletion Report | Akun yang di-delete per periode | Admin Ops+ |
| Spending per Client Report | Pengeluaran per siswa | Admin Ops, Parent |

### 19.3 Financial Reports

| Report | Deskripsi | Access Level |
|--------|-----------|-------------|
| Revenue Summary | Ringkasan revenue platform | Admin Hub+, SuperAdmin |
| Fee Breakdown | Detail fee per stream | Admin Hub+, SuperAdmin |
| Merchant Revenue Report | Revenue per merchant | Admin Ops+ |
| Reconciliation Report | Smart Access vs Winpay reconciliation | Admin Hub+, SuperAdmin |

### 19.4 Analytics

| Analytics | Deskripsi | Access Level |
|-----------|-----------|-------------|
| Peak Hours Analysis | Jam transaksi paling sibuk | Admin Ops+ |
| Top Products | Produk paling banyak dibeli | Admin Ops, Merchant |
| Top Merchants | Merchant dengan revenue tertinggi | Admin Ops+ |
| Spending Pattern per Class | Pola pengeluaran per kelas | Admin Ops+ |
| Enrollment Rate Tracking | Tren enrollment per periode | Admin Hub+, Admin Ops |
| Device Availability Rate | % device online vs offline | Admin Ops+ |

### 19.5 Export Requirements

**XLSX:**
- Multi-sheet jika perlu
- Freeze header
- Filterable columns
- Summary + detail tabs
- Numeric columns formatted

**PDF:**
- Company logo, report title, period
- Landscape untuk tabel lebar
- Summary section + detail section
- Generated by, generated at
- Pagination, total records

---

## 20. Exception Handling

### 20.1 Exception Registry

| Code | Exception | Handling |
|------|-----------|---------| 
| `EX-001` | Biometric match failure (FAR/FRR) | Retry 3x → fallback PIN → account lock setelah 3x PIN gagal |
| `EX-002` | Insufficient balance | Tolak transaksi, notif ke Parent, suggest top-up |
| `EX-003` | Daily limit exceeded | Tolak transaksi, notif ke Parent |
| `EX-004` | Winpay timeout/error | Retry mechanism, transaksi di-queue, alert ke Admin Ops |
| `EX-005` | Device offline > 24 jam | Force sync alert, disable offline transactions |
| `EX-006` | Overdraft saat sync | Suspend client account, notif Admin Ops, notif Parent untuk top-up |
| `EX-007` | Duplicate transaction (idempotency) | Detect via idempotency key → skip duplicate |
| `EX-008` | Account locked (3x PIN fail) | Auto-lock 15 menit, notif Parent + Admin Ops |
| `EX-009` | Device malfunction | Alert Admin Ops, switch ke spare device |
| `EX-010` | Biometric template outdated | Force re-enrollment, notif ke Admin Ops + Parent |
| `EX-011` | Payment expired (top-up timeout) | Mark as expired, notif Parent untuk retry |
| `EX-012` | Refund conflict (> 24 jam) | Tolak request, suggest resolution via ticket |
| `EX-013` | Unusual transaction pattern | Fraud alert ke Admin Ops, optional auto-suspend |
| `EX-014` | SLA breach (ticket unresolved) | Auto-escalate ke level atas |

### 20.2 Rules Engine

```
IF biometric_fail_count >= 3
  → FALLBACK ke PIN authentication

IF pin_fail_count >= 3
  → LOCK account for 15 minutes
  → NOTIFY parent + admin_ops

IF offline_duration > 24_hours
  → DISABLE offline transaction
  → FORCE sync alert

IF daily_spent >= daily_limit
  → REJECT transaction
  → NOTIFY parent

IF winpay_callback = failed
  → RETRY (max 3x, exponential backoff)
  → ALERT admin_ops if all retries fail

IF transaction_anomaly_detected
  → FLAG for review
  → NOTIFY admin_ops

IF sla_breach_detected
  → SEND notification to next level

IF biometric_age > 90_days
  → SEND re-enrollment reminder
```

---

## 21. Security & Access Control

### 21.1 Authentication

| Aspek | Detail |
|-------|--------|
| Method | JWT (short expiry: 1 jam) + Refresh Token (30 hari) |
| Provider | Supabase Auth |
| Password Policy | Bcrypt hashing, min 8 karakter, complexity requirements |
| Session | Auto-expire 30 menit inactivity, single-session enforcement |
| Rate Limiting | Max 5 failed login attempts → lock 15 menit |

### 21.2 Authorization

| Aspek | Detail |
|-------|--------|
| Model | Role-Based Access Control (RBAC) |
| Row Level Security | Supabase RLS — user hanya akses data sesuai school/region-nya |
| Scope-Based | User hanya akses data branch/regional-nya |

### 21.3 Approval Chain

| Action | Requestor | Approver |
|--------|-----------|----------|
| Buat Admin Hub | SuperAdmin | (direct) |
| Buat Admin Ops | Admin Hub | SuperAdmin |
| Approve Refund | Merchant/Parent | Admin Ops |
| Hapus Admin Ops | Admin Hub | SuperAdmin |
| Hapus Admin Hub | SuperAdmin | (direct, with confirmation) |
| Account Deletion | Admin Ops / Parent | (process with grace period) |

### 21.4 Data Protection (UU PDP No. 27/2022)

| Requirement | Implementation |
|-------------|---------------|
| **Consent** | Explicit written consent dari parent sebelum enrollment biometrik anak |
| **Purpose Limitation** | Data biometrik hanya untuk autentikasi pembayaran — tidak untuk tujuan lain |
| **Data Minimization** | Simpan template saja, bukan raw data biometrik |
| **Storage Limitation** | Hapus data biometrik saat akun di-delete atau siswa lulus |
| **Data Residency** | Semua data disimpan di server dalam wilayah Indonesia |
| **Right to Access** | Parent dapat melihat data apa saja yang tersimpan tentang anaknya |
| **Right to Delete** | Parent dapat request penghapusan data (grace period 14 hari) |
| **Breach Notification** | Wajib notifikasi ke pengguna dan otoritas dalam 3x24 jam jika terjadi breach |
| **DPO** | Menunjuk Data Protection Officer |
| **DPIA** | Melakukan Data Protection Impact Assessment sebelum launch |

### 21.5 Application Security

| Aspect | Standard |
|--------|---------|
| **API Security** | Rate limiting, input validation, parameterized queries |
| **Encryption in Transit** | TLS 1.3 minimum |
| **Encryption at Rest** | AES-256 untuk data sensitif (biometrik, credentials) |
| **XSS Prevention** | Output encoding |
| **CORS** | Whitelist allowed origins |
| **Vulnerability Assessment** | Penetration testing sebelum launch dan per 6 bulan |
| **OWASP** | Comply dengan OWASP Top 10 |
| **Code Security** | Dependency scanning, static code analysis di CI/CD |

### 21.6 Financial Security

| Aspect | Standard |
|--------|---------|
| **PCI-DSS** | Tidak menyimpan data kartu — compliance menjadi tanggung jawab Winpay |
| **Transaction Integrity** | Idempotency keys untuk prevent double-processing |
| **Reconciliation** | Daily automated reconciliation antara Smart Access ledger vs Winpay |
| **Fraud Detection** | Alert untuk transaksi anomali (unusual frequency, amount, time) |

### 21.7 Data Integrity

- Audit log append-only (tidak boleh edit/hapus)
- Transaction records immutable
- Soft delete untuk master entities
- Biometric data hard delete saat account deletion
- Investigation/ticket records tidak boleh dihapus

### 21.8 Backup & Recovery

- Database backup terjadwal (daily)
- Point-in-time recovery
- Transaction replay capability
- Export archive per periode

---

## 22. Hardware & Infrastructure

### 22.1 Biometric Device

| Parameter | Specification |
|-----------|---------------|
| **Fingerprint Sensor** | Capacitive / Optical, minimum 500 dpi |
| **Camera** | Minimum 2MP, IR-capable (low-light support) |
| **Display** | Minimum 5" — menampilkan status transaksi dan amount |
| **Connectivity** | WiFi (primary), 4G/LTE (backup), Ethernet (optional) |
| **Local Storage** | Minimum 8GB — offline template cache |
| **Battery/UPS** | Minimum 4 jam backup power |
| **OS** | Android 10+ atau custom embedded OS |
| **SDK** | Smart Access SDK terintegrasi |
| **Tampilan** | Menampilkan: nama client, foto, status match, amount |
| **OTA Update** | Over-the-air firmware dan SDK update |

### 22.2 Device Management

| Aspek | Detail |
|-------|--------|
| **Registration** | Device harus terdaftar di sistem sebelum digunakan |
| **Heartbeat** | Device kirim heartbeat per 5 menit |
| **Remote Wipe** | Capability untuk remote wipe data jika device hilang |
| **Remote Update** | OTA firmware update capability |
| **Monitoring** | Device health monitoring (battery, connectivity, storage) |

### 22.3 Network Requirements

- WiFi coverage di area sekolah (kantin, koperasi, dll)
- Mobile data (4G) sebagai backup connectivity
- Local buffering jika internet putus (offline mode)
- Sinkronisasi otomatis saat koneksi kembali
- Minimum bandwidth: 5 Mbps per device

---

## 23. KPI & Success Metrics

### 23.1 User Adoption KPIs

| KPI | Target | Deskripsi |
|-----|--------|-----------|
| Biometric Enrollment Rate | > 90% | % siswa ter-enroll di sekolah aktif |
| Daily Active Users | > 70% | % siswa aktif bertransaksi per hari |
| Parent App Adoption | > 80% | % parent yang install dan aktif di app |
| Merchant Participation Rate | > 90% | % merchant di sekolah yang aktif |

### 23.2 Transaction KPIs

| KPI | Target | Deskripsi |
|-----|--------|-----------|
| Biometric Match Success Rate | > 98% | Transaksi berhasil via biometric (bukan fallback) |
| Transaction Success Rate | > 99% | Semua transaksi (termasuk fallback) |
| Average Transaction Time | < 3 detik | Total waktu dari scan sampai receipt |
| Fallback PIN Usage Rate | < 5% | % transaksi menggunakan PIN (semakin rendah semakin baik) |
| Push Notification Delivery | ≤ 5 detik | Waktu notif sampai di parent |

### 23.3 Financial KPIs

| KPI | Target | Deskripsi |
|-----|--------|-----------|
| Settlement Success Rate | > 99.9% | Real-time settlement ke merchant |
| Reconciliation Accuracy | > 99.99% | Smart Access vs Winpay ledger match |
| Average Top-up Frequency | ≥ 2x/bulan | Frekuensi top-up per parent |
| Overdraft Rate (offline) | < 0.1% | % transaksi offline yang overdraft |
| Revenue per School (MRR) | TBD | Monthly recurring revenue per sekolah |

### 23.4 Support KPIs

| KPI | Target | Deskripsi |
|-----|--------|-----------|
| SLA Compliance Rate | > 95% | % ticket resolved dalam SLA |
| Ticket Resolution Time (L1) | < 24 jam | Admin Ops first-line |
| Customer Satisfaction (CSAT) | > 4.0/5.0 | Rating dari requester |
| Escalation Rate | < 10% | % ticket yang perlu eskalasi |

---

## 24. Non-Functional Requirements

### 24.1 Performance

| ID | Requirement | Target |
|----|-------------|-------|
| NFR-P-001 | Biometric match time | ≤ 2 detik (P95) |
| NFR-P-002 | API response time | ≤ 500ms (P95) |
| NFR-P-003 | Transaction processing (e2e) | ≤ 3 detik |
| NFR-P-004 | Push notification delivery | ≤ 5 detik |
| NFR-P-005 | Dashboard page load | ≤ 3 detik |
| NFR-P-006 | Concurrent transactions per school | 50 transaksi/menit |
| NFR-P-007 | Peak load handling | 500 transaksi/30 menit per school (jam istirahat) |

### 24.2 Scalability

| ID | Requirement | Target |
|----|-------------|-------|
| NFR-S-001 | Users per school | Hingga 5.000 clients |
| NFR-S-002 | Schools per region | Hingga 100 schools |
| NFR-S-003 | Regions | Hingga 50 regions |
| NFR-S-004 | Total capacity | 25.000.000 clients (target nasional jangka panjang) |
| NFR-S-005 | Transaction volume | 100.000 transaksi/hari per region |
| NFR-S-006 | Horizontal scaling | Multiple API instances |

### 24.3 Availability

| ID | Requirement | Target |
|----|-------------|-------|
| NFR-A-001 | System uptime | 99.5% (monthly) |
| NFR-A-002 | Planned maintenance window | Maks 4 jam, di luar jam sekolah (22:00-06:00) |
| NFR-A-003 | RTO (Recovery Time Objective) | ≤ 2 jam |
| NFR-A-004 | RPO (Recovery Point Objective) | ≤ 15 menit |
| NFR-A-005 | Offline mode availability | 24 jam tanpa internet |

### 24.4 Compatibility

| Platform | Minimum Version |
|----------|----------------|
| **Android** | Android 8.0 (Oreo) ke atas |
| **iOS** | iOS 14 ke atas |
| **Web Browser** | Chrome 90+, Firefox 88+, Safari 14+, Edge 90+ |
| **Biometric Device** | Android 10+ atau custom embedded OS |

### 24.5 Security

| ID | Requirement | Target |
|----|-------------|-------|
| NFR-SEC-001 | Data Encryption | TLS 1.3 in transit, AES-256 at rest |
| NFR-SEC-002 | SQL Injection Prevention | Parameterized queries |
| NFR-SEC-003 | XSS Prevention | Output encoding |
| NFR-SEC-004 | CORS | Whitelist allowed origins |
| NFR-SEC-005 | Rate Limiting | 100 req/min per user |

### 24.6 Compliance

| ID | Requirement | Target |
|----|-------------|-------|
| NFR-C-001 | Data Privacy | UU PDP No. 27/2022 compliance |
| NFR-C-002 | Audit Trail | Log all modifications, append-only |
| NFR-C-003 | Data Retention | 5 tahun transaksi, 7 tahun audit log |
| NFR-C-004 | Biometric Data | Consent-based, hard delete on account deletion |

---

## 25. Phasing & Roadmap

### 25.1 Phase Overview

```
Phase 1 (MVP)          Phase 2               Phase 3              Phase 4
Q3 2026                Q4 2026               Q1-Q2 2027           Q3-Q4 2027
┌─────────────┐       ┌─────────────┐       ┌─────────────┐      ┌─────────────┐
│ Core System │       │ Enhancement │       │ Scale       │      │ Advanced    │
│ & Pilot     │  ──▶ │ & Stability │  ──▶  │ & Growth    │ ──▶ │ Features    │
└─────────────┘       └─────────────┘       └─────────────┘      └─────────────┘
```

### 25.2 Phase 1 — MVP & Pilot (Target: Q3 2026)

**Objective:** Launch di 1-3 sekolah pilot untuk validasi konsep

| Module | Fitur |
|--------|-------|
| **Auth & RBAC** | Login, role-based access untuk semua roles |
| **User Management** | CRUD untuk semua entity (manual, bukan bulk) |
| **Biometric Enrollment** | Fingerprint + Face enrollment & matching |
| **Top Up** | Parent top-up via Winpay (QRIS & Transfer) |
| **Purchase Transaction** | Dual-biometric payment flow |
| **Fallback PIN** | PIN sebagai fallback autentikasi |
| **Real-time Notification** | Push notif transaksi ke parent |
| **Spending Limit** | Daily limit setting oleh parent |
| **Product Management** | CRUD produk oleh merchant |
| **Basic Dashboard** | Analytics dasar per role |
| **Audit Trail** | Activity logging |
| **Platform** | Web (admin) + Mobile (parent, merchant) + Biometric device |

**Excluded from Phase 1:**
- ❌ Offline mode
- ❌ Bulk enrollment (CSV)
- ❌ Virtual Account (VA)
- ❌ Export report (PDF/Excel)
- ❌ Scheduled reports
- ❌ Stock management
- ❌ Advanced analytics

### 25.3 Phase 2 — Enhancement & Stability (Target: Q4 2026)

| Module | Fitur |
|--------|-------|
| **Offline Mode** | Offline transaction capability dengan sync |
| **Bulk Enrollment (CSV)** | Import siswa via CSV |
| **Virtual Account (VA)** | Tambahan payment channel |
| **Support Ticketing** | Open ticket + SLA management |
| **Refund Mechanism** | Refund flow dengan approval Admin Ops |
| **Re-enrollment Reminder** | Auto-reminder per kuartal |
| **Export Report** | PDF & Excel export |
| **Account Deletion Flow** | 14-hari grace period + saldo pencairan |

### 25.4 Phase 3 — Scale & Growth (Target: Q1-Q2 2027)

| Module | Fitur |
|--------|-------|
| **Multi-region Rollout** | Onboard sekolah di multiple regions |
| **Advanced Analytics** | Detailed KPI dashboards per role |
| **Stock Management** | Inventory tracking untuk merchant |
| **Scheduled Reports** | Auto-generated reports via email |
| **Performance Optimization** | Handle peak loads di scale |
| **Fraud Detection** | Anomaly detection & alerting |

### 25.5 Phase 4 — Advanced Features (Target: Q3-Q4 2027)

| Module | Fitur |
|--------|-------|
| **Government Integration** | Support program makan gratis / subsidi |
| **Advanced Merchant Tools** | Promo, diskon, loyalty points |
| **Parent Advanced Controls** | Category-based spending limits, scheduled allowances |
| **API Public** | API untuk integrasi third-party |
| **Multi-language** | Support Bahasa Inggris (untuk international schools) |

---

## 26. API Specifications

### 26.1 API Design Principles

- RESTful API design
- JSON request/response format
- JWT Bearer token authentication
- Consistent error response format
- Pagination for list endpoints
- Rate limiting per user/IP
- Versioned API (v1, v2, etc.)

### 26.2 Base URL

```
Production: https://api.smartaccess.kgiton.com/v1
Staging:    https://api-staging.smartaccess.kgiton.com/v1
```

### 26.3 Core Endpoint Groups

| Group | Base Path | Deskripsi |
|-------|-----------|-----------| 
| Auth | `/auth/*` | Login, refresh, logout, me |
| Organizations | `/organizations/*` | Region, School CRUD |
| Users | `/users/*` | User CRUD, role assignment |
| Merchants | `/merchants/*` | Merchant management |
| Products | `/products/*` | Product catalog CRUD |
| Parents | `/parents/*` | Parent management |
| Clients | `/clients/*` | Client management, biometric status |
| Biometric | `/biometric/*` | Enrollment, re-enrollment, match |
| Transactions | `/transactions/*` | Top-up, purchase, refund |
| Tickets | `/tickets/*` | Support ticket management |
| Reports | `/reports/*` | Report generation & export |
| Notifications | `/notifications/*` | Notification management |
| Approvals | `/approvals/*` | Approval queue |
| Dashboard | `/dashboard/*` | Dashboard data per role |
| Devices | `/devices/*` | Biometric device management |
| Audit | `/audit/*` | Audit log access |

### 26.4 Authentication Flow

```json
// POST /auth/login
{
  "email": "admin@smartaccess.kgiton.com",
  "password": "securepassword"
}

// Response (200 OK)
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid",
      "email": "admin@smartaccess.kgiton.com",
      "full_name": "Admin Ops SDN 01",
      "role": "ADMIN_OPS",
      "entity": {
        "type": "SCHOOL",
        "id": "uuid",
        "name": "SDN 01 Bandung"
      }
    },
    "access_token": "eyJhbGc...",
    "refresh_token": "eyJhbGc...",
    "expires_in": 3600
  }
}
```

### 26.5 Error Response Format

```json
// 400 Bad Request
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": [
      { "field": "amount", "message": "Minimum top-up amount is Rp 10.000" }
    ]
  }
}

// 403 Forbidden
{
  "success": false,
  "error": {
    "code": "FORBIDDEN",
    "message": "Anda tidak memiliki akses ke resource ini"
  }
}

// 402 Payment Required
{
  "success": false,
  "error": {
    "code": "INSUFFICIENT_BALANCE",
    "message": "Saldo tidak mencukupi untuk transaksi ini"
  }
}

// 429 Too Many Requests
{
  "success": false,
  "error": {
    "code": "DAILY_LIMIT_EXCEEDED",
    "message": "Limit pengeluaran harian telah tercapai"
  }
}
```

### 26.6 Rate Limits

| Endpoint Category | Rate Limit | Window |
|-------------------|-----------|--------|
| Authentication | 10 requests | 1 minute |
| Biometric Operations | 50 requests | 1 minute |
| Transactions | 100 requests | 1 minute |
| Reports | 20 requests | 1 minute |
| Master Data | 50 requests | 1 minute |
| File Upload | 10 requests | 1 minute |

---

## 27. Glossary

| Istilah | Definisi |
|---------|---------|
| **Smart Access** | Platform teknologi pembayaran biometrik untuk satuan pendidikan |
| **Client** | Siswa / anak yang menggunakan biometrik untuk bertransaksi |
| **Parent / User** | Orang tua / wali yang mengelola akun dan saldo anak |
| **Admin Ops** | Admin Operations — administrator tingkat sekolah / cabang |
| **Admin Hub** | Administrator tingkat regional |
| **SuperAdmin** | Administrator tingkat nasional |
| **Merchant** | Pelaku usaha dalam ekosistem sekolah (kantin, laundry, minimarket, dll) |
| **Winpay** | Payment Gateway pihak ketiga yang memproses semua transaksi keuangan |
| **Dual-biometric** | Penggunaan dua metode biometrik (Fingerprint + Face Recognition) secara berurutan |
| **FAR** | False Acceptance Rate — persentase orang yang salah diterima oleh sistem |
| **FRR** | False Rejection Rate — persentase orang yang benar ditolak oleh sistem |
| **SLA** | Service Level Agreement — perjanjian tingkat layanan |
| **RBAC** | Role-Based Access Control — kontrol akses berbasis peran |
| **UU PDP** | Undang-Undang Perlindungan Data Pribadi (No. 27/2022) |
| **DPIA** | Data Protection Impact Assessment — penilaian dampak perlindungan data |
| **DPO** | Data Protection Officer — petugas perlindungan data |
| **PG** | Payment Gateway |
| **MDR** | Merchant Discount Rate — biaya yang dikenakan kepada merchant per transaksi |
| **VA** | Virtual Account — metode pembayaran via rekening virtual |
| **OTA** | Over-the-Air — update perangkat tanpa kabel fisik |
| **Escrow** | Dana yang ditahan oleh pihak ketiga (Winpay) sebelum disalurkan |
| **POS** | Point of Sale — tempat/sistem penjualan |
| **Fallback PIN** | 6-digit PIN sebagai alternatif autentikasi jika biometric gagal |
| **Settlement** | Proses penyelesaian/penyaluran dana dari transaksi ke merchant |
| **Overdraft** | Kondisi saldo minus yang terjadi akibat transaksi offline yang melebihi saldo aktual |
| **Idempotency Key** | Kunci unik untuk mencegah pemrosesan ganda pada transaksi yang sama |
| **Template Matching** | Proses pencocokan data biometrik yang tersimpan dengan input baru |
| **Liveness Detection** | Teknologi untuk mendeteksi apakah input biometrik berasal dari orang hidup (bukan foto/video/silikon) |

---

## Document Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-04-15 | KGiTON Team | Initial version — 19 sections |
| 1.1 | 2026-04-16 | KGiTON Team | Restructured to 27-section comprehensive format (aligned with LMS PRD standard), added Design Principles, Permission Matrix, Exception Handling, API Specs, KPI & Metrics, Dashboard detail |

---

*Document prepared for PT KGiTON — Smart Access Payment Transaction Platform*
*Confidential — Internal Use Only*
