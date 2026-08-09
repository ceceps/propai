import json
from decimal import Decimal
from typing import List, Optional
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

from models.property import Property, PropertyType, ListingStatus, ShowingRequest


class PropertyListingSystemDB:
    def __init__(self, db_connection_url: str):
        self.db_url = db_connection_url

    def get_connection(self):
        return psycopg2.connect(self.db_url)

    def create_listing(self, property_data: dict, agent_id: str) -> dict:
        query = """
            INSERT INTO properties (
                mls_number, property_type, address, listing_price, bedrooms,
                bathrooms, square_feet, lot_size, year_built, description,
                features, photos, status, listing_agent_id, coordinates
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, point(%s, %s)
            ) RETURNING property_id, mls_number, created_at;
        """
        import uuid
        mls_number = f"MLS-{uuid.uuid4().hex[:10].upper()}"
        coords = property_data.get('coordinates', (0.0, 0.0))

        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (
                    mls_number,
                    property_data['property_type'],
                    json.dumps(property_data['address']),
                    Decimal(str(property_data['price'])),
                    property_data['bedrooms'],
                    property_data['bathrooms'],
                    property_data['square_feet'],
                    property_data.get('lot_size', 0),
                    property_data['year_built'],
                    property_data['description'],
                    property_data.get('features', []),
                    property_data.get('photos', []),
                    ListingStatus.ACTIVE.value,
                    agent_id,
                    coords[0], coords[1]
                ))
                res = cur.fetchone()
                conn.commit()
                return dict(res)

    def search_properties(self, criteria: dict) -> List[dict]:
        conditions = ["status = %s"]
        params = [ListingStatus.ACTIVE.value]

        if 'min_price' in criteria:
            conditions.append("listing_price >= %s")
            params.append(Decimal(str(criteria['min_price'])))
        if 'max_price' in criteria:
            conditions.append("listing_price <= %s")
            params.append(Decimal(str(criteria['max_price'])))
        if 'min_bedrooms' in criteria:
            conditions.append("bedrooms >= %s")
            params.append(criteria['min_bedrooms'])
        if 'min_bathrooms' in criteria:
            conditions.append("bathrooms >= %s")
            params.append(criteria['min_bathrooms'])
        if 'min_sqft' in criteria:
            conditions.append("square_feet >= %s")
            params.append(criteria['min_sqft'])
        if 'property_type' in criteria:
            conditions.append("property_type = %s")
            params.append(criteria['property_type'])

        order_by = "listing_date DESC"
        if criteria.get('sort_by') == 'price_asc':
            order_by = "listing_price ASC"
        elif criteria.get('sort_by') == 'price_desc':
            order_by = "listing_price DESC"

        where_clause = " AND ".join(conditions)
        query = f"SELECT * FROM properties WHERE {where_clause} ORDER BY {order_by};"

        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params)
                return [dict(row) for row in cur.fetchall()]
