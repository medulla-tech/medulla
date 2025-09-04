CREATE TABLE IF NOT EXISTS inventories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    machine_id TEXT NOT NULL,
    package_name TEXT,
    version TEXT,
    vendor TEXT,
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
