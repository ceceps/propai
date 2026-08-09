from datetime import datetime
from propai_api.system import PropertyListingSystem
from models.property import PropertyType, ListingStatus

def test_system():
    pls = PropertyListingSystem()

    # 1. Test create listing
    data = {
        'property_type': 'single_family',
        'address': {'street': '123 Main St'},
        'price': 500000,
        'bedrooms': 3,
        'bathrooms': 2,
        'square_feet': 2000,
        'year_built': 2020,
        'description': 'Nice house',
        'coordinates': (37.7749, -122.4194)
    }
    prop = pls.create_listing(data, agent_id='AGENT-1')
    assert prop.property_id.startswith('PROP-')
    assert prop.listing_price == 500000
    assert prop.status == ListingStatus.ACTIVE

    # 2. Test search
    results = pls.search_properties({'min_price': 400000, 'max_price': 600000})
    assert len(results) == 1

    # 3. Test price per sqft
    ppsqft = pls.calculate_price_per_sqft(prop)
    assert ppsqft == 250

    # 4. Test schedule showing
    res = pls.schedule_showing(prop.property_id, 'BUYER-AGENT-1', 'John', datetime.now())
    assert res.get('success') is True

    print("ALL TESTS PASSED")

if __name__ == '__main__':
    test_system()
