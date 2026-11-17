from flask import Flask, redirect, render_template, request, url_for
import sqlite3

from parking import (
    count_free,
    distinct_status_events,
    filter_expiring_spaces,
    get_avg_price,
    get_free_space,
    get_occupied_spaces,
    map_space_labels,
    occupy_space_in_db,
    process_event_tick,
    scan_parking_revenue,
    validate_parking_hours,
)

app = Flask(__name__)


@app.route('/')
def start():
  return render_template('index.html')


@app.route('/parking')
def statistics():
  conn = sqlite3.connect('data.db')
  conn.row_factory = sqlite3.Row
  cursor = conn.cursor()

  cursor.execute('SELECT * FROM spaces')
  current_mesta = [dict(row) for row in cursor.fetchall()]

  cursor.execute('SELECT * FROM tariffs')
  current_tariffs = [dict(row) for row in cursor.fetchall()]
  conn.close()

  tick_mesta = process_event_tick(current_mesta)
  sample_payments = [{'price': 500}, {'price': 800}, {'price': 300}]
  sample_events = [
      {'status': 'free'},
      {'status': 'free'},
      {'status': 'occupied'},
  ]

  return render_template(
      'parking.html',
      total=len(tick_mesta),
      free=get_free_space(tick_mesta),
      occupied=get_occupied_spaces(tick_mesta),
      data=tick_mesta,
      avg_price=get_avg_price(current_tariffs),
      free_count=count_free(tick_mesta),
      expiring=filter_expiring_spaces(current_mesta, 1),
      labels=map_space_labels(tick_mesta),
      revenue=scan_parking_revenue(sample_payments),
      events=distinct_status_events(sample_events),
  )


@app.route('/select-hours/<int:space_id>')
def select_hours(space_id):
  return render_template('select_hours.html', space_id=space_id)


@app.route('/occupy-with-hours/<int:space_id>', methods=['POST'])
def occupy_with_hours(space_id):
  hours_str = request.form.get('hours')
  result = validate_parking_hours(hours_str)

  if result.is_right:
    occupy_space_in_db(space_id, result.value)

  return redirect(url_for('statistics'))


if __name__ == '__main__':
  app.run(debug=True)