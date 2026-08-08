"""Role-based access control, enforced at the query layer.

The matrix below is AGENTS.md's, transcribed:

    Module            Super Admin   Property Agent   Freelance Agent
    Manage Listings   CRUD All      CRUD Own         Read Only
    Scraping Data     Full Access   No Access        No Access
    Leads Data        All Data      Own Leads        Own Leads
    Agency Analytics  Full Access   Own Stats        No Access

Scoping lives here, not in route handlers or templates, so a hand-crafted API
call cannot reach another agent's rows by skipping the UI.
"""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import Select

from propai_core.models.users import User, UserRole

if TYPE_CHECKING:
    pass


class Module(StrEnum):
    LISTINGS = "listings"
    SCRAPING = "scraping"
    LEADS = "leads"
    ANALYTICS = "analytics"


class Action(StrEnum):
    READ = "read"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


# (module, action) -> roles permitted. Absence means denied.
_MATRIX: dict[tuple[Module, Action], frozenset[UserRole]] = {
    (Module.LISTINGS, Action.READ): frozenset(
        {UserRole.ADMIN, UserRole.AGENT, UserRole.FREELANCE}
    ),
    (Module.LISTINGS, Action.CREATE): frozenset({UserRole.ADMIN, UserRole.AGENT}),
    (Module.LISTINGS, Action.UPDATE): frozenset({UserRole.ADMIN, UserRole.AGENT}),
    (Module.LISTINGS, Action.DELETE): frozenset({UserRole.ADMIN, UserRole.AGENT}),
    (Module.SCRAPING, Action.READ): frozenset({UserRole.ADMIN}),
    (Module.SCRAPING, Action.CREATE): frozenset({UserRole.ADMIN}),
    (Module.SCRAPING, Action.UPDATE): frozenset({UserRole.ADMIN}),
    (Module.SCRAPING, Action.DELETE): frozenset({UserRole.ADMIN}),
    (Module.LEADS, Action.READ): frozenset(
        {UserRole.ADMIN, UserRole.AGENT, UserRole.FREELANCE}
    ),
    (Module.LEADS, Action.UPDATE): frozenset(
        {UserRole.ADMIN, UserRole.AGENT, UserRole.FREELANCE}
    ),
    (Module.LEADS, Action.CREATE): frozenset({UserRole.ADMIN, UserRole.AGENT}),
    (Module.LEADS, Action.DELETE): frozenset({UserRole.ADMIN}),
    (Module.ANALYTICS, Action.READ): frozenset({UserRole.ADMIN, UserRole.AGENT}),
}


def can(user: User, module: Module, action: Action) -> bool:
    """Coarse role check. Row ownership is a separate concern, see scope_*."""
    return user.role in _MATRIX.get((module, action), frozenset())


def scope_properties(stmt: Select, user: User) -> Select:
    """Admin sees all. Agent and freelance see only their own rows.

    Freelance is read-only on listings, which `can()` enforces; the scoping is
    the same, so a freelance agent can never even read another agent's listing.
    """
    from propai_core.models.properties import Property

    if user.role is UserRole.ADMIN:
        return stmt
    return stmt.where(Property.owner_id == user.id)


def scope_leads(stmt: Select, user: User) -> Select:
    """Admin sees all leads. Everyone else sees only leads assigned to them."""
    from propai_core.models.leads import Lead

    if user.role is UserRole.ADMIN:
        return stmt
    return stmt.where(Lead.assigned_agent_id == user.id)


def owns_property(user: User, owner_id) -> bool:
    return user.role is UserRole.ADMIN or user.id == owner_id
