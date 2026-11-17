import json
from collections import Counter
from itertools import islice
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
    make_cost_calculator,
    occupy_space_by_id_rec,
    check_space_status_rec,
    get_zone_occupancy_cached,
    get_free_ids_rec,
    save_json_data,
    Either,
    validate_parking_hours,
    occupy_space_in_db,
    iter_long_sessions,
    running_avg_hours,
    lazy_zone_load,
    take,
    first_free_spot
)

# Патч для Either, чтобы код из parking.py успешно создавал объекты без ошибок
def _patched_init(self, value=None, is_right=None):
    self.value = value
    self.is_right = is_right

Either.__init__ = _patched_init

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


def test_occupy_space_by_id_rec():
    local_mesta = [
        {"id": 1, "status": "free"},
        {"id": 2, "status": "free"},
    ]
    updated_mesta = occupy_space_by_id_rec(local_mesta, space_id=2)
    assert updated_mesta[1]["status"] == "occupied"
    assert updated_mesta[0]["status"] == "free"
    assert local_mesta[1]["status"] == "free"


def test_check_space_status_rec():
    local_mesta = [
        {"id": 101, "status": "free"},
        {"id": 102, "status": "occupied"},
    ]
    assert check_space_status_rec(local_mesta, 101) == "free"
    assert check_space_status_rec(local_mesta, 102) == "occupied"
    assert check_space_status_rec(local_mesta, 999) == "not_found"


def test_get_zone_occupancy_cached():
    assert get_zone_occupancy_cached(10, 5) == 50.0
    assert get_zone_occupancy_cached(3, 1) == 33.3
    assert get_zone_occupancy_cached(0, 0) == 0.0


def test_get_free_ids_rec():
    local_mesta = [
        {"id": "A1", "status": "free"},
        {"id": "A2", "status": "occupied"},
        {"id": "B1", "status": "free"},
    ]
    assert get_free_ids_rec(local_mesta) == ["A1", "B1"]

    all_occupied = [{"id": "C1", "status": "occupied"}]
    assert get_free_ids_rec(all_occupied) == []


def test_validate_parking_hours_success():
    result = validate_parking_hours("5")
    assert result.is_right is True
    assert result.value == 5


def test_validate_parking_hours_zero():
    result = validate_parking_hours("0")
    assert result.is_right is False
    assert result.value == "Часы должны быть больше нуля"


def test_validate_parking_hours_negative():
    result = validate_parking_hours("-3")
    assert result.is_right is False
    assert result.value == "Часы должны быть больше нуля"


def test_validate_parking_hours_invalid_format():
    result = validate_parking_hours("abc")
    assert result.is_right is False
    assert result.value == "Неверный формат числа"


def test_either_left_creation():
    err_container = Either.left("Тестовая ошибка")
    assert err_container.is_right is False
    assert err_container.value == "Тестовая ошибка"







def test_iter_long_sessions():
    sessions = [
        {"id": 1, "hours": 2},
        {"id": 2, "hours": 5},
        {"id": 3, "hours": 3},
    ]
    result = list(iter_long_sessions(sessions, min_hours=3))
    assert len(result) == 2
    assert result[0]["id"] == 2
    assert result[1]["id"] == 3


def test_running_avg_hours():
    sessions = [
        {"hours": 2},
        {"hours": 4},
        {"hours": 6},
    ]
    result = list(running_avg_hours(sessions))
    assert result == [2.0, 3.0, 4.0]



def test_lazy_zone_load():
    sessions = [
        {"space": "A1"},
        {"space": "A2"},
        {"space": "B1"},
    ]
    zone_of = {"A1": "Zone A", "A2": "Zone A", "B1": "Zone B"}
    result = list(lazy_zone_load(sessions, zone_of))
    assert result == [
        {"Zone A": 1},
        {"Zone A": 2},
        {"Zone A": 2, "Zone B": 1},
    ]



def test_take():
    items = [10, 20, 30, 40, 50]
    result = list(take(3, items))
    assert result == [10, 20, 30]


def test_first_free_spot():
    spaces_with_free = [
        {"number": 1, "status": "occupied"},
        {"number": 2, "status": "free"},
        {"number": 3, "status": "free"},
    ]
    spot = first_free_spot(spaces_with_free)
    assert spot is not None
    assert spot["number"] == 2

    all_occupied = [
        {"number": 1, "status": "occupied"},
        {"number": 2, "status": "occupied"},
    ]
    assert first_free_spot(all_occupied) is None











from parking import (
    distinct_status_events,
    filter_expiring_spaces,
    map_space_labels,
    process_event_tick,
    scan_parking_revenue,
)


def test_process_event_tick():
  mesta = [{'id': 1, 'status': 'occupied', 'hours': 1}]
  res = process_event_tick(mesta)
  assert res[0]['hours'] == 0
  assert res[0]['status'] == 'free'


def test_filter_expiring_spaces():
  mesta = [
      {'id': 1, 'status': 'occupied', 'hours': 1},
      {'id': 2, 'status': 'occupied', 'hours': 5},
  ]
  assert len(filter_expiring_spaces(mesta, 1)) == 1


def test_map_space_labels():
  mesta = [{'number': 1, 'status': 'free'}]
  assert map_space_labels(mesta) == ['№1-free']


def test_scan_parking_revenue():
  payments = [{'price': 100}, {'price': 200}]
  assert scan_parking_revenue(payments) == [100, 300]


def test_distinct_status_events():
  events = [{'status': 'free'}, {'status': 'free'}, {'status': 'occupied'}]
  res = distinct_status_events(events)
  assert len(res) == 2
  assert res[0]['status'] == 'free'
  assert res[1]['status'] == 'occupied'

