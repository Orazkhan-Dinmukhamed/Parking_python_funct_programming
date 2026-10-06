from flask import Flask, render_template, redirect, url_for
import json

# Импортируем твои старые функции И новые (с рекурсией и сохранением)
from parking import (
    get_number_free_spaces, 
    get_free_space, 
    amount_of_places,
    zones, 
    mesta, 
    get_occupied_spaces, 
    get_all_price,
    get_avg_price, 
    count_free, 
    tariffs,
    occupy_space_by_id_rec,  
    save_json_data           
)

app = Flask(__name__)

@app.route("/")
def start():
    return render_template('index.html')

@app.route('/parking')
def statistics():
    
    with open('parking.json', 'r', encoding='utf-8') as f:
        json_data = json.load(f)
        
    current_mesta = json_data['spaces']
    current_tariffs = json_data['tariffs']
    
    total = len(current_mesta)
    free = get_free_space(current_mesta)
    occupied = get_occupied_spaces(current_mesta)
    avg_price = get_avg_price(current_tariffs)
    free_count = count_free(current_mesta)

    return render_template(
        'parking.html',
        total=total,
        free=free,
        occupied=occupied,
        data=current_mesta,
        avg_price=avg_price,
        free_count=free_count
    )


@app.route('/occupy/<int:space_id>', methods=['POST'])
def occupy_single_space(space_id):
    with open('parking.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    
    data['spaces'] = occupy_space_by_id_rec(data['spaces'], space_id)
    
    
    save_json_data('parking.json', data)
    
    return redirect(url_for('statistics'))

if __name__ == '__main__':
    app.run(debug=True)