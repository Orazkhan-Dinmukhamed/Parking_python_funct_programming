from parking import (
    get_free_space,
    get_occupied_spaces,
    get_number_free_spaces,
    get_zones_names,
    get_spaces_by_zone_id,
    get_all_numbers,
    get_all_price,
    get_avg_price,
    count_free,
    amount_of_places,
    make_cost_calculator
)

mesta = [
    {"number": 1, "status": "free", "zone_id": "A"},
    {"number": 2, "status": "occupied", "zone_id": "A"},
    {"number": 3, "status": "free", "zone_id": "B"},
    {"number": 4, "status": "occupied", "zone_id": "B"},
    {"number": 5, "status": "free", "zone_id": "C"},
]

zones = [
    {"id": "A", "name": "Zone A"},
    {"id": "B", "name": "Zone B"},
    {"id": "C", "name": "Zone C"},
]

tariffs = [
    {"price_per_hour": 500},
    {"price_per_hour": 800},
    {"price_per_hour": 300},
]


def test_get_free_space():
    assert len(get_free_space(mesta)) == 3


def test_get_occupied_spaces():
    assert len(get_occupied_spaces(mesta)) == 2


def test_get_number_free_spaces():
    assert get_number_free_spaces(mesta) == [1, 3, 5]


def test_get_zones_names():
    assert get_zones_names(zones) == ["Zone A", "Zone B", "Zone C"]


def test_get_spaces_by_zone_id():
    result = get_spaces_by_zone_id(mesta, "A")
    assert get_all_numbers(result) == [1, 2]


def test_get_all_numbers():
    assert get_all_numbers(mesta) == [1, 2, 3, 4, 5]

def test_count_free():
    assert count_free(mesta) == 3


def test_get_all_price():
    assert get_all_price(tariffs) == 1600


def test_get_avg_price():
    assert get_avg_price(tariffs) == 533.33


def test_amount_of_places():
    assert amount_of_places() == 10



