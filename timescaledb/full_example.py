import psycopg2
from psycopg2.extras import execute_values

CONNECTION = "postgres://postgres:password@localhost:5432/postgres"

if __name__ == "__main__":
    with psycopg2.connect(CONNECTION) as conn:
        c = conn.cursor()

        # Create a normal PostgreSQL table
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS sensors_series (
                apparent_time TIMESTAMPTZ NOT NULL,
                id INTEGER NOT NULL,
                source VARCHAR(50),
                measurement REAL
            );
            SELECT create_hypertable('sensors_series', 'apparent_time', chunk_time_interval => INTERVAL '1 week', if_not_exists => TRUE);
            """
        )
        
        # Create a TimescaleDB hypertable
        c.execute(
            """
            SELECT create_hypertable('sensors_series', 'apparent_time', chunk_time_interval => INTERVAL '1 week', if_not_exists => TRUE);
            """
        )
        c.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        print("--- Tables ---")
        print(c.fetchall())

        # Insert records efficiently
        records = [
            ("2016-06-22 19:10:27-00", 4, "temperature", 23.3),
            ("2016-06-22 19:11:23-00", 5, "temperature", 23.4),
            ("2016-06-22 19:16:02-00", 9, "pressue", 1029.3),
            ("2016-06-22 19:21:43-00", 10, "temperature", 23.6),
            ("2016-06-22 19:33:01-00", 11, "temperature", 24.0),
            ("2016-06-22 19:34:53-00", 12, "temperature", 25.0),
        ]
        execute_values(
            c,
            """
            INSERT INTO SENSORS_SERIES (apparent_time, id, source, measurement)
            VALUES %s;
            """,
            records,
            template=None,
            page_size=100,
        )

        # Select all records
        c.execute(
            """
            SELECT * from sensors_series;
            """
        )
        print("\n--- Records ---")
        for row in c.fetchall():
            print(row)

        # Select records aggregated by time
        c.execute(
            """
            SELECT
                time_bucket('5 minutes', apparent_time) + '5 minutes' AS five_min,
                avg(measurement)
            FROM sensors_series
            WHERE source = 'temperature'
            GROUP BY five_min;
            """
        )
        print("\n--- Aggregated records ---")
        for row in c.fetchall():
            print(row)

        # Drop the table (and associated hypertable)
        c.execute(
            """
            DROP TABLE sensors_series;
            """
        )
        c.close()
