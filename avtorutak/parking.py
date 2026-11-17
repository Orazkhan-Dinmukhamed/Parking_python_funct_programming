from collections import Counter
from functools import lru_cache, reduce
from itertools import islice
import random
import sqlite3
import threading


conn = sqlite3.connect('data.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute('SELECT * FROM spaces')
mesta = [dict(row) for row in cursor.fetchall()]

cursor.execute('SELECT * FROM zones')
zones = [dict(row) for row in cursor.fetchall()]

cursor.execute('SELECT * FROM tariffs')
tariffs = [dict(row) for row in cursor.fetchall()]

conn.close()

MESTA = tuple(mesta)
ZONES = tuple(zones)
TARIFFS = tuple(tariffs)


def get_all_price(tariffs):
  return reduce(lambda acc, t: acc + t['price_per_hour'], tariffs, 0)


def get_avg_price(tariffs):
  return round(get_all_price(tariffs) / len(tariffs), 2)


def make_cost_calculator(price_per_hour):
  return lambda hours: round(hours * price_per_hour, 2)


vip_tariff_price = tariffs[0]['price_per_hour']
calculate_vip_cost = make_cost_calculator(vip_tariff_price)
print(calculate_vip_cost(2))


def count_free(mesta, i=0):
  if i >= len(mesta):
    return 0
  return (mesta[i]['status'] == 'free') + count_free(mesta, i + 1)


def get_free_space(mesta):
  return list(filter(lambda x: x['status'] == 'free', mesta))


def get_occupied_spaces(mesta):
  return list(filter(lambda x: x['status'] == 'occupied', mesta))


def get_number_free_spaces(mesta):
  return list(map(lambda x: x['number'], get_free_space(mesta)))


def get_zones_names(zones):
  return list(map(lambda zone: zone['name'], zones))


def get_spaces_by_zone_id(mesta, id):
  return list(filter(lambda x: x['zone_id'] == id, mesta))


def get_all_numbers(mesta):
  return list(map(lambda x: x['number'], mesta))


all_place_num = get_all_numbers(mesta)


def amount_of_places():
  return len(all_place_num)


print(amount_of_places())


def occupy_space_by_id_rec(mesta, space_id, i=0):
  if i >= len(mesta):
    return []
  current = dict(mesta[i])
  if current['id'] == space_id:
    current['status'] = 'occupied'
  return [current] + occupy_space_by_id_rec(mesta, space_id, i + 1)


def check_space_status_rec(mesta, space_id, i=0):
  if i >= len(mesta):
    return 'not_found'
  if mesta[i]['id'] == space_id:
    return mesta[i]['status']
  return check_space_status_rec(mesta, space_id, i + 1)


@lru_cache(maxsize=None)
def get_zone_occupancy_cached(total_in_zone, occupied_in_zone):
  if total_in_zone == 0:
    return 0.0
  return round((occupied_in_zone / total_in_zone) * 100, 1)


def get_free_ids_rec(mesta, i=0):
  if i >= len(mesta):
    return []
  rest = get_free_ids_rec(mesta, i + 1)
  if mesta[i]['status'] == 'free':
    return [mesta[i]['id']] + rest
  return rest


def save_json_data(file_path, full_data):
  conn = sqlite3.connect('data.db')
  cursor = conn.cursor()
  for space in full_data.get('spaces', []):
    cursor.execute(
        'UPDATE spaces SET status = ? WHERE id = ?',
        (space['status'], space['id']),
    )
  conn.commit()
  conn.close()


print('Cashed zone=', get_zone_occupancy_cached(100, 37))
print('free space id=', get_free_ids_rec(mesta, i=0))





class Either:

  def __init__(self, value, is_right=True):
    self.value = value
    self.is_right = is_right

  @staticmethod
  def right(val):
    return Either(val, True)

  @staticmethod
  def left(err):
    return Either(err, False)


def validate_parking_hours(hours_str):
  try:
    h = int(hours_str)
    if h > 0:
      return Either.right(h)
    return Either.left('Часы должны быть больше нуля')
  except ValueError:
    return Either.left('Неверный формат числа')



def occupy_space_in_db(space_id, hours):
  conn = sqlite3.connect('data.db')
  cursor = conn.cursor()
  cursor.execute(
      "UPDATE spaces SET status = 'occupied', hours = ? WHERE id = ?",
      (hours, space_id),
  )
  conn.commit()
  conn.close()

  
  def reset_space():
    db_conn = sqlite3.connect('data.db')
    cur = db_conn.cursor()
    cur.execute(
        "UPDATE spaces SET status = 'free', hours = 0 WHERE id = ?", (space_id,)
    )
    db_conn.commit()
    db_conn.close()

  timer = threading.Timer(10.0,reset_space)
  timer.start()






def iter_long_sessions(sessions, min_hours):
  for s in sessions:
    if s['hours'] >= min_hours:
      yield s


def running_avg_hours(sessions):
  total = 0
  count = 0
  for s in sessions:
    total += s['hours']
    count += 1
    yield round(total / count, 2)


def lazy_zone_load(sessions, zone_of):
  counts = Counter()
  for s in sessions:
    counts[zone_of[s['space']]] += 1
    yield dict(counts)


def take(n, iterable):
  yield from islice(iterable, n)


def first_free_spot(spaces):
  return next((s for s in spaces if s['status'] == 'free'), None)







def process_event_tick(mesta):
  res = []
  for m in mesta:
    item = dict(m)
    if item.get('status') == 'occupied':
      item['hours'] = max(0, item.get('hours', 0) - 1)
      if item['hours'] == 0:
        item['status'] = 'free'
    res.append(item)
  return res



def filter_expiring_spaces(mesta, limit=1):
  return list(
      filter(
          lambda m: m.get('status') == 'occupied'
          and m.get('hours', 0) <= limit,
          mesta,
      )
  )


def map_space_labels(mesta):
  return list(map(lambda m: f"№{m['number']}-{m['status']}", mesta))


def scan_parking_revenue(payments):
  acc, res = 0, []
  for p in payments:
    acc += p.get('price', 0)
    res.append(acc)
  return res


def distinct_status_events(events):
  res = []
  for e in events:
    if not res or res[-1]['status'] != e['status']:
      res.append(e)
  return res