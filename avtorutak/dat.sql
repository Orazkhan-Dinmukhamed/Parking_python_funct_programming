CREATE TABLE IF NOT EXISTS zones (
    id INTEGER PRIMARY KEY,
    name TEXT,
    description TEXT
);

CREATE TABLE IF NOT EXISTS spaces (
    id INTEGER PRIMARY KEY,
    number TEXT,
    zone_id INTEGER,
    status TEXT,
    hours INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS tariffs (
    id INTEGER PRIMARY KEY,
    name TEXT,
    zone_id INTEGER,
    price_per_hour INTEGER
);

INSERT OR IGNORE INTO zones (id, name, description) VALUES 
(1, 'A', 'Основная зона'),
(2, 'B', 'Бизнес-зона'),
(3, 'C', 'Эконом-зона');

INSERT OR IGNORE INTO spaces (id, number, zone_id, status, hours) VALUES 
(1, 'A-01', 1, 'free', 0),
(2, 'A-02', 1, 'free', 0),
(3, 'A-03', 1, 'free', 0),
(4, 'A-04', 1, 'free', 0),
(5, 'B-01', 2, 'free', 0),
(6, 'B-02', 2, 'free', 0),
(7, 'B-03', 2, 'free', 0),
(8, 'C-01', 3, 'free', 0),
(9, 'C-02', 3, 'free', 0),
(10, 'C-03', 3, 'free', 0);

INSERT OR IGNORE INTO tariffs (id, name, zone_id, price_per_hour) VALUES 
(1, 'Standard', 1, 500),
(2, 'Business', 2, 800),
(3, 'Economy', 3, 300);