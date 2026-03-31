"""
reset_db.py — Drop all tables and re-run Alembic migrations from scratch.
Also creates a default platform_admin account.

Usage:
    python reset_db.py                         # interactive confirmation
    python reset_db.py --yes                   # skip confirmation prompt
    python reset_db.py --yes --seed            # reset + seed platform admin
"""

import asyncio
import argparse
import sys
from getpass import getpass

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# ── Load app config & models ──────────────────────────────────────────────────
from app.config import settings
from app.core.database import Base

# Import every model so Base.metadata knows all tables
from app.models.merchant import Merchant          # noqa: F401
from app.models.outlet import Outlet              # noqa: F401
from app.models.device import Device              # noqa: F401
from app.models.customer import Customer          # noqa: F401
from app.models.wallet import Wallet, WalletLedger  # noqa: F401
from app.models.transaction import Transaction    # noqa: F401
from app.models.biometric import FaceCredential, FingerprintCredential  # noqa: F401
from app.models.audit import AuditLog             # noqa: F401
from app.models.user import User                  # noqa: F401
from app.models.firmware import FirmwareVersion   # noqa: F401


# ── Helpers ───────────────────────────────────────────────────────────────────

def _confirm(prompt: str) -> bool:
    answer = input(f"{prompt} [y/N]: ").strip().lower()
    return answer == "y"


async def drop_all(engine) -> None:
    """Drop all application tables using SQLAlchemy metadata."""
    async with engine.begin() as conn:
        # Drop the alembic_version table too so migrations start clean
        await conn.execute(
            text("DROP TABLE IF EXISTS alembic_version CASCADE")
        )
        await conn.run_sync(Base.metadata.drop_all)
    print("  ✓ All tables dropped.")


async def create_all(engine) -> None:
    """Recreate all tables via SQLAlchemy (schema-only, no Alembic stamp)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("  ✓ All tables recreated.")


async def stamp_alembic(engine) -> None:
    """Stamp alembic_version to the latest revision so future migrations work."""
    import subprocess
    result = subprocess.run(
        ["alembic", "stamp", "head"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"  ⚠ alembic stamp head failed:\n{result.stderr}")
    else:
        print("  ✓ Alembic version stamped to head.")


async def seed_platform_admin(engine, email: str, password: str, name: str) -> None:
    """Insert a platform_admin user."""
    from app.core.security import hash_password
    from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
    from sqlalchemy import select

    AsyncSession_ = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with AsyncSession_() as session:
        # Check if already exists
        result = await session.execute(select(User).where(User.email == email))
        existing = result.scalar_one_or_none()
        if existing:
            print(f"  ⚠ User '{email}' already exists — skipping seed.")
            return

        admin = User(
            email=email,
            hashed_password=hash_password(password),
            name=name,
            role="platform_admin",
        )
        session.add(admin)
        await session.commit()
        print(f"  ✓ Platform admin created: {email}")


# ── Main ──────────────────────────────────────────────────────────────────────

async def main(skip_confirm: bool, seed: bool) -> None:
    print("\n=== Biometric Payment API — Database Reset ===\n")
    print(f"  Target: {settings.DATABASE_URL.split('@')[-1]}")  # hide credentials
    print()

    if not skip_confirm:
        print("  ⚠️  WARNING: This will DROP and RECREATE all tables.")
        print("  All existing data will be permanently deleted.")
        print()
        if not _confirm("Are you sure you want to reset the database?"):
            print("  Aborted.")
            sys.exit(0)

    engine = create_async_engine(settings.DATABASE_URL, echo=False)

    try:
        print("\n[1/3] Dropping all tables...")
        await drop_all(engine)

        print("\n[2/3] Recreating tables...")
        await create_all(engine)

        print("\n[3/3] Stamping Alembic revision...")
        await stamp_alembic(engine)

        if seed:
            print("\n[Seed] Creating platform admin account...")
            print("  (Leave blank to skip)")
            name = input("  Admin name   : ").strip()
            if not name:
                print("  Skipped.")
            else:
                email = input("  Admin email  : ").strip()
                password = getpass("  Password     : ")
                if not email or not password:
                    print("  ⚠ Email or password empty — skipped.")
                else:
                    await seed_platform_admin(engine, email, password, name)

        print("\n✅  Database reset complete.\n")

    finally:
        await engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reset the biometric payment database.")
    parser.add_argument(
        "--yes", "-y",
        action="store_true",
        help="Skip the confirmation prompt.",
    )
    parser.add_argument(
        "--seed",
        action="store_true",
        help="Interactively create a platform_admin user after reset.",
    )
    args = parser.parse_args()

    asyncio.run(main(skip_confirm=args.yes, seed=args.seed))
