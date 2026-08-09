from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from enum import Enum


class PropertyType(Enum):
    SINGLE_FAMILY = "single_family"
    CONDO = "condo"
    TOWNHOUSE = "townhouse"
    MULTI_FAMILY = "multi_family"
    LAND = "land"
    COMMERCIAL = "commercial"


class ListingStatus(Enum):
    ACTIVE = "active"
    PENDING = "pending"
    SOLD = "sold"
    WITHDRAWN = "withdrawn"
    EXPIRED = "expired"


@dataclass
class Property:
    property_id: str
    mls_number: str
    property_type: PropertyType
    address: dict
    listing_price: Decimal
    bedrooms: int
    bathrooms: float
    square_feet: int
    lot_size: float
    year_built: int
    description: str
    features: List[str]
    photos: List[str]
    status: ListingStatus
    listing_date: datetime
    listing_agent_id: str
    coordinates: tuple


@dataclass
class ShowingRequest:
    showing_id: str
    property_id: str
    buyer_agent_id: str
    buyer_name: str
    requested_date: datetime
    duration_minutes: int
    status: str
    notes: str