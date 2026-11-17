from functools import lru_cache, reduce
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

  timer = threading.Timer(10.0, reset_space)
  timer.start()


