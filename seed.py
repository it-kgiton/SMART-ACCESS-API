"""
seed.py — Inject full PRD role hierarchy seed data.

Hirarki: Region → School → Merchant / Parent → Client

Akun yang dibuat:
  super_admin : superadmin@smartaccess.id  / Admin@12345
  admin_hub   : adminhub@smartaccess.id    / Admin@12345
  admin_ops   : adminops@smartaccess.id    / Admin@12345
  merchant    : merchant@smartaccess.id    / Admin@12345
  parent      : parent@smartaccess.id      / Admin@12345

Usage:
    python seed.py
    python seed.py --yes   # skip konfirmasi
"""

import asyncio
import argparse
import uuid
from datetime import datetime, timezone

import asyncpg
import bcrypt as _bcrypt

from app.config import settings


def _get_dsn() -> str:
    dsn = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    if "?" in dsn:
        base, params = dsn.split("?", 1)
        keep = [p for p in params.split("&")
                if not p.startswith("prepared_statement_cache_size")]
        dsn = base + ("?" + "&".join(keep) if keep else "")
    return dsn


def _hash(password: str) -> str:
    return _bcrypt.hashpw(password.encode("utf-8"), _bcrypt.gensalt(12)).decode("utf-8")


def _uid() -> str:
    return str(uuid.uuid4())


async def main(skip_confirm: bool) -> None:
    print("\n=== SmartAccess — Seed Data Injection ===\n")
    print(f"  Target: {settings.DATABASE_URL.split('@')[-1]}\n")

    if not skip_confirm:
        ans = input("  Lanjutkan inject seed data? [y/N]: ").strip().lower()
        if ans != "y":
            print("  Dibatalkan.")
            return

    conn = await asyncpg.connect(_get_dsn(), statement_cache_size=0)
    now = datetime.now(timezone.utc)
    pw = "Admin@12345"
    hashed_pw = _hash(pw)

    try:
        # ── 1. Region ──
        region_id = _uid()
        row = await conn.fetchrow("SELECT id FROM regions WHERE region_code = $1", "REG-JATIM-001")
        if row:
            region_id = str(row["id"])
            print("  ⚠  Region REG-JATIM-001 sudah ada — skip.")
        else:
            await conn.execute(
                """INSERT INTO regions (id, region_code, region_name, province, status, created_at, updated_at)
                   VALUES ($1, $2, $3, $4, $5, $6, $6)""",
                region_id, "REG-JATIM-001", "Regional Jawa Timur", "Jawa Timur", "active", now,
            )
            print("  ✓  Region: Regional Jawa Timur (REG-JATIM-001)")

        # ── 2. Super Admin ──
        sa_email = "superadmin@smartaccess.id"
        row = await conn.fetchrow("SELECT id FROM users WHERE email = $1", sa_email)
        if row:
            print(f"  ⚠  [{sa_email}] sudah ada — skip.")
        else:
            sa_id = _uid()
            await conn.execute(
                """INSERT INTO users (id, email, hashed_password, full_name, phone, role, is_active, created_at, updated_at)
                   VALUES ($1, $2, $3, $4, $5, $6, true, $7, $7)""",
                sa_id, sa_email, hashed_pw, "Super Admin", "08000000000", "super_admin", now,
            )
            print(f"  ✓  [super_admin] Super Admin ({sa_email})")

        # ── 3. Admin Hub (linked to region) ──
        ah_email = "adminhub@smartaccess.id"
        row = await conn.fetchrow("SELECT id FROM users WHERE email = $1", ah_email)
        if row:
            ah_id = str(row["id"])
            print(f"  ⚠  [{ah_email}] sudah ada — skip.")
        else:
            ah_id = _uid()
            await conn.execute(
                """INSERT INTO users (id, email, hashed_password, full_name, phone, role, region_id, is_active, created_at, updated_at)
                   VALUES ($1, $2, $3, $4, $5, $6, $7, true, $8, $8)""",
                ah_id, ah_email, hashed_pw, "Admin Hub Jawa Timur", "08000000001", "admin_hub", region_id, now,
            )
            print(f"  ✓  [admin_hub] Admin Hub Jawa Timur ({ah_email})")

        # Update region admin_user_id
        await conn.execute("UPDATE regions SET admin_user_id = $1 WHERE id = $2", ah_id, region_id)

        # ── 4. School ──
        school_id = _uid()
        row = await conn.fetchrow("SELECT id FROM schools WHERE school_code = $1", "SDN-SBY-001")
        if row:
            school_id = str(row["id"])
            print("  ⚠  School SDN-SBY-001 sudah ada — skip.")
        else:
            await conn.execute(
                """INSERT INTO schools (id, region_id, school_code, school_name, school_type, address, phone, email, status, created_at, updated_at)
                   VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $10)""",
                school_id, region_id, "SDN-SBY-001", "SDN Surabaya 001", "sd",
                "Jl. Pahlawan No. 10, Surabaya", "031-11111111", "sdn001@surabaya.sch.id",
                "active", now,
            )
            print("  ✓  School: SDN Surabaya 001 (SDN-SBY-001)")

        # ── 5. Admin Ops (linked to school) ──
        ao_email = "adminops@smartaccess.id"
        row = await conn.fetchrow("SELECT id FROM users WHERE email = $1", ao_email)
        if row:
            print(f"  ⚠  [{ao_email}] sudah ada — skip.")
        else:
            ao_id = _uid()
            await conn.execute(
                """INSERT INTO users (id, email, hashed_password, full_name, phone, role, school_id, is_active, created_at, updated_at)
                   VALUES ($1, $2, $3, $4, $5, $6, $7, true, $8, $8)""",
                ao_id, ao_email, hashed_pw, "Admin Ops SDN Surabaya 001", "08000000002", "admin_ops", school_id, now,
            )
            print(f"  ✓  [admin_ops] Admin Ops SDN Surabaya 001 ({ao_email})")

        # ── 6. Merchant + merchant user ──
        m_email = "merchant@smartaccess.id"
        row = await conn.fetchrow("SELECT id FROM users WHERE email = $1", m_email)
        if row:
            print(f"  ⚠  [{m_email}] sudah ada — skip.")
        else:
            merchant_id = _uid()
            m_user_id = _uid()
            await conn.execute(
                """INSERT INTO users (id, email, hashed_password, full_name, phone, role, school_id, merchant_id, is_active, created_at, updated_at)
                   VALUES ($1, $2, $3, $4, $5, $6, $7, $8, true, $9, $9)""",
                m_user_id, m_email, hashed_pw, "Pedagang Demo", "08123456789", "merchant",
                school_id, merchant_id, now,
            )
            await conn.execute(
                """INSERT INTO merchants (id, user_id, school_id, business_name, business_type, status, balance, created_at, updated_at)
                   VALUES ($1, $2, $3, $4, $5, $6, 0, $7, $7)""",
                merchant_id, m_user_id, school_id, "Warung Demo SmartAccess", "kantin", "active", now,
            )
            print(f"  ✓  [merchant] Pedagang Demo ({m_email})")

        # ── 7. Parent + parent record ──
        p_email = "parent@smartaccess.id"
        row = await conn.fetchrow("SELECT id FROM users WHERE email = $1", p_email)
        if row:
            print(f"  ⚠  [{p_email}] sudah ada — skip.")
        else:
            parent_id = _uid()
            p_user_id = _uid()
            await conn.execute(
                """INSERT INTO users (id, email, hashed_password, full_name, phone, role, school_id, is_active, created_at, updated_at)
                   VALUES ($1, $2, $3, $4, $5, $6, $7, true, $8, $8)""",
                p_user_id, p_email, hashed_pw, "Orang Tua Demo", "08111111111", "parent", school_id, now,
            )
            await conn.execute(
                """INSERT INTO parents (id, user_id, school_id, name, phone, email, daily_limit_default, created_at, updated_at)
                   VALUES ($1, $2, $3, $4, $5, $6, 50000, $7, $7)""",
                parent_id, p_user_id, school_id, "Orang Tua Demo", "08111111111", p_email, now,
            )

            # ── 8. Client (student) + wallet ──
            client_id = _uid()
            wallet_id = _uid()
            await conn.execute(
                """INSERT INTO clients (id, user_id, parent_id, school_id, name, student_id_number, class_name, grade,
                   daily_spending_limit, biometric_enrolled, balance, status, created_at, updated_at)
                   VALUES ($1, NULL, $2, $3, $4, $5, $6, $7, 25000, false, 0, 'active', $8, $8)""",
                client_id, parent_id, school_id, "Anak Demo", "NIS-SDN-001", "6A", "6", now,
            )
            await conn.execute(
                """INSERT INTO wallets (id, client_id, balance, status, created_at, updated_at)
                   VALUES ($1, $2, 0, 'active', $3, $3)""",
                wallet_id, client_id, now,
            )
            print(f"  ✓  [parent] Orang Tua Demo ({p_email})")
            print(f"     → Client: Anak Demo (NIS-SDN-001) + Wallet")

    finally:
        await conn.close()

    print("\n✅  Selesai!\n")
    print(f"  Password semua akun: {pw}\n")
    accounts = [
        ("super_admin", "superadmin@smartaccess.id"),
        ("admin_hub", "adminhub@smartaccess.id"),
        ("admin_ops", "adminops@smartaccess.id"),
        ("merchant", "merchant@smartaccess.id"),
        ("parent", "parent@smartaccess.id"),
    ]
    print(f"  {'Role':<20} {'Email':<38}")
    print(f"  {'-'*20} {'-'*38}")
    for role, email in accounts:
        print(f"  {role:<20} {email:<38}")
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--yes", "-y", action="store_true")
    args = parser.parse_args()
    asyncio.run(main(skip_confirm=args.yes))
