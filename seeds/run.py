"""Seed the database with synthetic Jawa Barat data.

Usage:
    python -m seeds.run            # purge seed-owned rows, then insert
    python -m seeds.run --purge    # purge only
    python -m seeds.run --keep     # insert without purging first

Purge is deliberately narrow: it removes only rows owned by accounts under
SEED_DOMAIN, plus documents whose titles match the seed corpus. Rows created by
a human through the UI are never touched, so running this against a database
with real work in it cannot destroy that work.
"""

from __future__ import annotations

import argparse
import sys

from sqlalchemy import delete, select

from propai_core.db import session_scope
from propai_core.models.properties import Property
from propai_core.models.rag import Document
from propai_core.models.users import User, UserRole
from propai_core.security import hash_password
from seeds.data import DOCUMENTS, PROPERTIES, SEED_DOMAIN, USERS


def purge_seed_data() -> dict[str, int]:
    """Remove only seed-owned rows. Returns counts for reporting."""
    removed = {"properties": 0, "users": 0, "documents": 0}

    with session_scope() as session:
        seed_user_ids = list(
            session.scalars(select(User.id).where(User.email.like(f"%@{SEED_DOMAIN}")))
        )

        if seed_user_ids:
            # Properties first: users.id is referenced with ondelete=RESTRICT,
            # so removing the owner before its listings would raise.
            result = session.execute(
                delete(Property).where(Property.owner_id.in_(seed_user_ids))
            )
            removed["properties"] = result.rowcount or 0

            result = session.execute(delete(User).where(User.id.in_(seed_user_ids)))
            removed["users"] = result.rowcount or 0

        seed_titles = [d["title"] for d in DOCUMENTS]
        result = session.execute(delete(Document).where(Document.title.in_(seed_titles)))
        removed["documents"] = result.rowcount or 0

    return removed


def seed() -> dict[str, int]:
    """Insert users, properties, and RAG documents. Returns counts."""
    counts = {"users": 0, "properties": 0, "documents": 0}

    with session_scope() as session:
        by_key: dict[str, User] = {}
        for spec in USERS:
            user = User(
                email=spec["email"],
                full_name=spec["full_name"],
                role=UserRole(spec["role"]),
                password_hash=hash_password(spec["password"]),
                whatsapp_number=spec.get("whatsapp_number"),
            )
            session.add(user)
            by_key[spec["email"].split("@")[0]] = user
            counts["users"] += 1
        session.flush()

        for spec in PROPERTIES:
            owner = by_key[spec["owner_key"]]
            session.add(
                Property(
                    title=spec["title"],
                    description=spec.get("description"),
                    price=spec["price"],
                    location=spec["location"],
                    status=spec["status"],
                    specs=spec["specs"],
                    owner_id=owner.id,
                )
            )
            counts["properties"] += 1

        for spec in DOCUMENTS:
            # Chunking and embedding happen in the RAG phase, not here: this
            # step must stay runnable with no LLM credentials present.
            session.add(
                Document(title=spec["title"], lang=spec["lang"], source_path="seeds/data.py")
            )
            counts["documents"] += 1

    return counts


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Seed PropAI with Jawa Barat demo data")
    parser.add_argument("--purge", action="store_true", help="purge seed rows and exit")
    parser.add_argument("--keep", action="store_true", help="skip the purge step")
    args = parser.parse_args(argv)

    if not args.keep:
        removed = purge_seed_data()
        print(
            f"purged: {removed['properties']} properties, "
            f"{removed['users']} users, {removed['documents']} documents"
        )
    if args.purge:
        return 0

    counts = seed()
    print(
        f"seeded: {counts['users']} users, {counts['properties']} properties, "
        f"{counts['documents']} documents"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
