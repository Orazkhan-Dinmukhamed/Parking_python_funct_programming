import json
from functools import reduce
from functools import lru_cache

with open('parking.json', 'r', encoding='utf-8') as fail:
    json_data = json.load(fail)

mesta = json_data['spaces']
zones = json_data['zones']  
tariffs = json_data['tariffs']

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
total = calculate_vip_cost(2)  

print(total)

def count_free(mesta, i=0):
    if i >= len(mesta):
        return 0
    return (mesta[i]['status'] == 'free') + count_free(mesta, i + 1)

def get_free_space(mesta):
    free_space = list(filter(lambda x:x['status'] == 'free', mesta))
    return free_space

def get_occupied_spaces(mesta):
    occupied = list(filter(lambda x:x['status'] == 'occupied', mesta))
    return occupied

def get_number_free_spaces(mesta):
    get = list(map(lambda x:x['number'], get_free_space(mesta)))
    return get

def get_zones_names(zones):
    return list(map(lambda zone: zone["name"], zones))

def get_spaces_by_zone_id(mesta, id):
    get = list(filter(lambda x:x['zone_id'] == id, mesta))
    return get

def get_all_numbers(mesta):
    all = list(map(lambda x:x['number'], mesta))
    return all

all_place_num = get_all_numbers(mesta)

def amount_of_places():
    all = len(all_place_num)
    return all

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
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(full_data, f, ensure_ascii=False, indent=4)
