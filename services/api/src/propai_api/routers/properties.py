"""Listings CRUD, scoped by RBAC at the query layer."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from propai_api.deps import CurrentUser, SessionDep, require
from propai_api.schemas import PropertyCreate, PropertyOut, PropertyUpdate
from propai_core.models.properties import Property
from propai_core.rbac import Action, Module, scope_properties

router = APIRouter(prefix="/properties", tags=["properties"])

_NOT_FOUND = HTTPException(status.HTTP_404_NOT_FOUND, "Property not found")


def _get_scoped(session, user, property_id: uuid.UUID) -> Property:
    """Fetch within the caller's scope.

    Returns 404 rather than 403 when the row exists but belongs to someone
    else: a 403 would confirm the id is real, letting an agent enumerate a
    rival's portfolio by probing ids.
    """
    stmt = (
        scope_properties(select(Property).where(Property.id == property_id), user)
        .options(selectinload(Property.photos))
    )
    prop = session.scalar(stmt)
    if prop is None:
        raise _NOT_FOUND
    return prop


@router.get("", response_model=list[PropertyOut])
def list_properties(
    session: SessionDep,
    user: Annotated[object, Depends(require(Module.LISTINGS, Action.READ))],
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
) -> list[Property]:
    stmt = scope_properties(select(Property), user).options(selectinload(Property.photos))
    stmt = stmt.order_by(Property.created_at.desc()).limit(limit).offset(offset)
    return list(session.scalars(stmt))


@router.post("", response_model=PropertyOut, status_code=status.HTTP_201_CREATED)
def create_property(
    payload: PropertyCreate,
    session: SessionDep,
    user: Annotated[object, Depends(require(Module.LISTINGS, Action.CREATE))],
) -> Property:
    prop = Property(**payload.model_dump(), owner_id=user.id)
    session.add(prop)
    session.flush()
    return prop


@router.get("/{property_id}", response_model=PropertyOut)
def get_property(
    property_id: uuid.UUID,
    session: SessionDep,
    user: Annotated[object, Depends(require(Module.LISTINGS, Action.READ))],
) -> Property:
    return _get_scoped(session, user, property_id)


@router.patch("/{property_id}", response_model=PropertyOut)
def update_property(
    property_id: uuid.UUID,
    payload: PropertyUpdate,
    session: SessionDep,
    user: Annotated[object, Depends(require(Module.LISTINGS, Action.UPDATE))],
) -> Property:
    prop = _get_scoped(session, user, property_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(prop, field, value)
    session.flush()
    return prop


@router.delete("/{property_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_property(
    property_id: uuid.UUID,
    session: SessionDep,
    user: Annotated[object, Depends(require(Module.LISTINGS, Action.DELETE))],
) -> None:
    session.delete(_get_scoped(session, user, property_id))
