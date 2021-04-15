CREATE TABLE IF NOT EXISTS sensors_series (
    apparent_time TIMESTAMPTZ NOT NULL,
    id INTEGER NOT NULL, 
    source VARCHAR(50),
    measurement REAL
);

SELECT create_hypertable('sensors_series', 'apparent_time', chunk_time_interval => INTERVAL '1 week', if_not_exists => TRUE);
