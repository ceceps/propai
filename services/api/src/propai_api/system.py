from datetime import datetime
from decimal import Decimal
from typing import List
import uuid
from math import radians, sin, cos, sqrt, atan2

from models.property import Property, PropertyType, ListingStatus, ShowingRequest


class PropertyListingSystem:
    def __init__(self):
        self.properties = {}
        self.showings = []
        self.saved_searches = {}

    def create_listing(self, property_data: dict, agent_id: str) -> Property:
        property_id = f"PROP-{uuid.uuid4().hex[:8].upper()}"
        mls_number = f"MLS-{uuid.uuid4().hex[:10].upper()}"

        property_obj = Property(
            property_id=property_id,
            mls_number=mls_number,
            property_type=PropertyType(property_data['property_type']),
            address=property_data['address'],
            listing_price=Decimal(str(property_data['price'])),
            bedrooms=property_data['bedrooms'],
            bathrooms=property_data['bathrooms'],
            square_feet=property_data['square_feet'],
            lot_size=property_data.get('lot_size', 0),
            year_built=property_data['year_built'],
            description=property_data['description'],
            features=property_data.get('features', []),
            photos=property_data.get('photos', []),
            status=ListingStatus.ACTIVE,
            listing_date=datetime.now(),
            listing_agent_id=agent_id,
            coordinates=property_data.get('coordinates', (0, 0))
        )

        self.properties[property_id] = property_obj
        return property_obj

    def search_properties(self, criteria: dict) -> List[Property]:
        results = []

        for prop in self.properties.values():
            if prop.status != ListingStatus.ACTIVE:
                continue

            if 'min_price' in criteria and prop.listing_price < Decimal(str(criteria['min_price'])):
                continue
            if 'max_price' in criteria and prop.listing_price > Decimal(str(criteria['max_price'])):
                continue
            if 'min_bedrooms' in criteria and prop.bedrooms < criteria['min_bedrooms']:
                continue
            if 'min_bathrooms' in criteria and prop.bathrooms < criteria['min_bathrooms']:
                continue
            if 'min_sqft' in criteria and prop.square_feet < criteria['min_sqft']:
                continue
            if 'property_type' in criteria and prop.property_type.value != criteria['property_type']:
                continue

            if 'location' in criteria and 'radius_miles' in criteria:
                distance = self._calculate_distance(prop.coordinates, criteria['location'])
                if distance > criteria['radius_miles']:
                    continue

            results.append(prop)

        if criteria.get('sort_by') == 'price_asc':
            results.sort(key=lambda p: p.listing_price)
        elif criteria.get('sort_by') == 'price_desc':
            results.sort(key=lambda p: p.listing_price, reverse=True)
        elif criteria.get('sort_by') == 'newest':
            results.sort(key=lambda p: p.listing_date, reverse=True)

        return results

    def schedule_showing(self, property_id: str, buyer_agent_id: str, buyer_name: str, requested_date: datetime) -> dict:
        prop = self.properties.get(property_id)
        if not prop:
            return {'error': 'Property not found'}

        if prop.status != ListingStatus.ACTIVE:
            return {'error': 'Property not available for showings'}

        conflicts = self._check_showing_conflicts(property_id, requested_date)
        if conflicts:
            return {'error': 'Time slot not available', 'conflicts': conflicts}

        showing_id = f"SHOW-{uuid.uuid4().hex[:8].upper()}"
        showing = ShowingRequest(
            showing_id=showing_id,
            property_id=property_id,
            buyer_agent_id=buyer_agent_id,
            buyer_name=buyer_name,
            requested_date=requested_date,
            duration_minutes=30,
            status='pending',
            notes=''
        )

        self.showings.append(showing)

        return {
            'success': True,
            'showing_id': showing.showing_id,
            'status': 'pending_confirmation'
        }

    def calculate_price_per_sqft(self, property_obj: Property) -> Decimal:
        if property_obj.square_feet == 0:
            return Decimal('0')

        price_per_sqft = property_obj.listing_price / property_obj.square_feet
        return price_per_sqft.quantize(Decimal('0.01'))

    def generate_cma(self, subject_property: Property, radius_miles: float = 1.0) -> dict:
        comparables = []

        for prop in self.properties.values():
            if prop.property_id == subject_property.property_id:
                continue
            if prop.property_type != subject_property.property_type:
                continue
            if prop.status != ListingStatus.SOLD:
                continue

            days_since_sale = (datetime.now() - prop.listing_date).days
            if days_since_sale > 180:
                continue

            distance = self._calculate_distance(subject_property.coordinates, prop.coordinates)
            if distance > radius_miles:
                continue

            size_diff = abs(prop.square_feet - subject_property.square_feet)
            if size_diff / subject_property.square_feet > 0.2:
                continue

            if abs(prop.bedrooms - subject_property.bedrooms) > 1:
                continue

            comparables.append(prop)

        if not comparables:
            return {'error': 'No comparable properties found'}

        prices = [float(p.listing_price) for p in comparables]
        price_per_sqft_values = [float(self.calculate_price_per_sqft(p)) for p in comparables]

        avg_price = sum(prices) / len(prices)
        avg_price_per_sqft = sum(price_per_sqft_values) / len(price_per_sqft_values)
        estimated_value = avg_price_per_sqft * subject_property.square_feet

        return {
            'subject_property_id': subject_property.property_id,
            'comparable_count': len(comparables),
            'comparables': [
                {
                    'property_id': p.property_id,
                    'address': p.address,
                    'price': float(p.listing_price),
                    'square_feet': p.square_feet,
                    'price_per_sqft': float(self.calculate_price_per_sqft(p))
                }
                for p in comparables[:5]
            ],
            'market_statistics': {
                'average_price': avg_price,
                'average_price_per_sqft': avg_price_per_sqft,
                'min_price': min(prices),
                'max_price': max(prices)
            },
            'estimated_value': estimated_value,
            'suggested_listing_price': estimated_value * 0.98
        }

    def save_search(self, user_id: str, search_criteria: dict) -> str:
        search_id = f"SEARCH-{uuid.uuid4().hex[:8].upper()}"
        self.saved_searches[search_id] = {
            'user_id': user_id,
            'criteria': search_criteria,
            'created_at': datetime.now(),
            'active': True
        }
        return search_id

    def _calculate_distance(self, coord1: tuple, coord2: tuple) -> float:
        lat1, lon1 = radians(coord1[0]), radians(coord1[1])
        lat2, lon2 = radians(coord2[0]), radians(coord2[1])

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        return 3959 * c

    def _check_showing_conflicts(self, property_id: str, requested_date: datetime) -> List[dict]:
        conflicts = []
        for showing in self.showings:
            if showing.property_id != property_id or showing.status == 'cancelled':
                continue

            time_diff = abs((showing.requested_date - requested_date).total_seconds() / 3600)
            if time_diff < 1:
                conflicts.append({
                    'showing_id': showing.showing_id,
                    'time': showing.requested_date.isoformat()
                })

        return conflicts