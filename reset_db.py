"""
reset_db.py — Drop all tables (including PostgreSQL enum types) and recreate
              schema from SQLAlchemy metadata. Uses statement_cache_size=0 to
              be safe with both Supabase session and transaction poolers.

Usage:
    python reset_db.py            # interactive confirmation
    python reset_db.py --yes      # skip confirmation prompt
"""

import asyncio
import argparse
import sys

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# ── Load app config & models ──────────────────────────────────────────────────
from app.config import settings
from app.core.database import Base

# Import every model so Base.metadata knows all tables
from app.models import (  # noqa: F401
    User, Region, School, Merchant, Product, Parent, Client,
    Wallet, WalletLedger, FaceCredential, FingerprintCredential,
    Transaction, TransactionItem, Device, Ticket, Notification,
    ApprovalRequest, AuditLog, FirmwareVersion,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _confirm(prompt: str) -> bool:
    answer = input(f"{prompt} [y/N]: ").strip().lower()
    return answer == "y"


async def drop_all(engine) -> None:
    async with engine.begin() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS alembic_version CASCADE"))
        await conn.run_sync(Base.metadata.drop_all)
        # Explicitly drop PostgreSQL enum types leftover from old schema
        await conn.execute(text("DROP TYPE IF EXISTS userrole CASCADE"))
        await conn.execute(text("DROP TYPE IF EXISTS transactionstatus CASCADE"))
        await conn.execute(text("DROP TYPE IF EXISTS biometricmode CASCADE"))
    print("  ✓ All tables and enum types dropped.")


async def create_all(engine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("  ✓ All tables recreated.")


async def stamp_alembic() -> None:
    import subprocess
    result = subprocess.run(
        ["alembic", "stamp", "head"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"  ⚠ alembic stamp head failed (non-critical):\n{result.stderr.strip()}")
    else:
        print("  ✓ Alembic version stamped to head.")


# ── Main ──────────────────────────────────────────────────────────────────────

async def main(skip_confirm: bool) -> None:
    print("\n=== SmartAccess — Database Reset ===\n")
    print(f"  Target: {settings.DATABASE_URL.split('@')[-1]}")
    print()

    if not skip_confirm:
        print("  ⚠️  WARNING: This will DROP and RECREATE all tables.")
        print("  ALL existing data will be permanently deleted.")
        print()
        if not _confirm("Are you sure?"):
            print("  Aborted.")
            sys.exit(0)

    # statement_cache_size=0 prevents DuplicatePreparedStatementError on pgbouncer
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        connect_args={"statement_cache_size": 0},
    )

    try:
        print("\n[1/3] Dropping all tables and enum types...")
        await drop_all(engine)

        print("\n[2/3] Recreating tables...")
        await create_all(engine)

        print("\n[3/3] Stamping Alembic revision...")
        await stamp_alembic()

        print("\n✅  Database reset complete.")
        print("    Run 'python seed.py --yes' to inject seed accounts.\n")

    finally:
        await engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reset the SmartAccess database.")
    parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation.")
    args = parser.parse_args()

    asyncio.run(main(skip_confirm=args.yes))
