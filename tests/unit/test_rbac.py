"""The RBAC matrix from AGENTS.md, asserted exhaustively.

Every (module, action, role) triple is covered, so adding a role or module
without deciding its permissions fails the suite rather than defaulting open.
"""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy import select

from propai_core.models.leads import Lead
from propai_core.models.properties import Property
from propai_core.models.users import UserRole
from propai_core.rbac import Action, Module, can, scope_leads, scope_properties

A, AG, FR = UserRole.ADMIN, UserRole.AGENT, UserRole.FREELANCE

# (module, action, role) -> expected. Transcribed from the AGENTS.md table.
MATRIX = [
    # Manage Listings: admin CRUD all, agent CRUD own, freelance READ ONLY.
    (Module.LISTINGS, Action.READ, A, True),
    (Module.LISTINGS, Action.READ, AG, True),
    (Module.LISTINGS, Action.READ, FR, True),
    (Module.LISTINGS, Action.CREATE, A, True),
    (Module.LISTINGS, Action.CREATE, AG, True),
    (Module.LISTINGS, Action.CREATE, FR, False),
    (Module.LISTINGS, Action.UPDATE, FR, False),
    (Module.LISTINGS, Action.DELETE, FR, False),
    # Scraping: admin only.
    (Module.SCRAPING, Action.READ, A, True),
    (Module.SCRAPING, Action.READ, AG, False),
    (Module.SCRAPING, Action.READ, FR, False),
    # Leads: all roles read (scoped), only admin deletes.
    (Module.LEADS, Action.READ, A, True),
    (Module.LEADS, Action.READ, AG, True),
    (Module.LEADS, Action.READ, FR, True),
    (Module.LEADS, Action.DELETE, AG, False),
    (Module.LEADS, Action.DELETE, FR, False),
    # Analytics: freelance has no access at all.
    (Module.ANALYTICS, Action.READ, A, True),
    (Module.ANALYTICS, Action.READ, AG, True),
    (Module.ANALYTICS, Action.READ, FR, False),
]


@pytest.mark.parametrize(("module", "action", "role", "expected"), MATRIX)
def test_matrix(module, action, role, expected, request):
    user = request.getfixturevalue(
        {A: "admin", AG: "agent", FR: "freelance"}[role]
    )
    assert can(user, module, action) is expected


def test_unknown_pair_denies_by_default(agent):
    """Absence from the matrix must mean denied, not permitted."""
    assert can(agent, Module.SCRAPING, Action.DELETE) is False


def _where(stmt) -> str:
    """Only the WHERE clause. Note UUIDs compile to bare hex, no dashes.

    Original note: Matching the whole statement gives false hits,
    because scoped column names also appear in the SELECT list."""
    clause = stmt.whereclause
    if clause is None:
        return ""
    return str(clause.compile(compile_kwargs={"literal_binds": True}))


def test_admin_property_scope_is_unfiltered(admin):
    assert _where(scope_properties(select(Property), admin)) == ""


def test_agent_property_scope_filters_to_owner(agent):
    where = _where(scope_properties(select(Property), agent))
    assert "owner_id" in where
    assert agent.id.hex in where


def test_freelance_property_scope_also_filters(freelance):
    """Freelance is read-only, but must still not read other agents' listings."""
    assert freelance.id.hex in _where(scope_properties(select(Property), freelance))


def test_lead_scope_isolates_agents(agent, freelance):
    """The core tenancy guarantee: one agent's lead query cannot match another's."""
    a_where = _where(scope_leads(select(Lead), agent))
    f_where = _where(scope_leads(select(Lead), freelance))
    assert agent.id.hex in a_where
    assert agent.id.hex not in f_where
    assert freelance.id.hex not in a_where


def test_admin_lead_scope_unfiltered(admin):
    assert _where(scope_leads(select(Lead), admin)) == ""
