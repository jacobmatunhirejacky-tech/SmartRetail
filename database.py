import psycopg2


DB_NAME = "local_sales.db"

# Paste your Neon PostgreSQL connection string here or pass connection variables directly
NEON_DATABASE_URL = "postgresql://user:YOUR_PASSWORD@ep-cool-cloud.neon.tech/neondb?sslmode=require"


def init_db():
    """Initializes the local SQLite database table."""
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id TEXT PRIMARY KEY,
            laptop_model TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL,
            timestamp TEXT NOT NULL,
            is_synced INTEGER DEFAULT 0
        )
    ''')

    connection.commit()
    connection.close()
    print("Local SQLite database initialized successfully.")



import sqlite3
import uuid
from datetime import datetime, timezone, timedelta

def add_sale(laptop_model, price, quantity):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    sale_id = str(uuid.uuid4())
    harare_tz = timezone(timedelta(hours=2))
    local_now = datetime.now(harare_tz).strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute('''
        INSERT INTO sales (id, laptop_model, price, quantity, timestamp)
        VALUES (?, ?, ?, ?, ?)
    ''', (sale_id, laptop_model, price, quantity, local_now))

    connection.commit()
    connection.close()

    # Return clean Python dictionary
    return {
        'id': sale_id,
        'laptop_model': laptop_model,
        'price': price,
        'quantity': quantity,
        'timestamp': local_now,
        'is_synced': 0
    }


def get_all_sales():
    """Fetches all local sales ordered by newest first."""
    connection = sqlite3.connect(DB_NAME)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute('SELECT * FROM sales ORDER BY timestamp DESC')
    sales = cursor.fetchall()

    connection.close()
    return sales


def get_unsynced_sales():
    """Fetches unsynced local rows."""
    connection = sqlite3.connect(DB_NAME)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute('SELECT * FROM sales WHERE is_synced = 0')
    rows = cursor.fetchall()

    connection.close()
    return rows


def mark_as_synced(sale_ids):
    """Updates local SQLite status flags to 1 once Neon commits."""
    if not sale_ids:
        return
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.executemany('UPDATE sales SET is_synced = 1 WHERE id = ?', [(s_id,) for s_id in sale_ids])

    connection.commit()
    connection.close()


def sync_to_neon():
    """Pushes unsynced local records to Neon cloud server using connection timeout handling."""
    unsynced = get_unsynced_sales()
    if not unsynced:
        return "Database up to date."

    neon_conn = None
    try:
        # Connect to Neon Cloud with a 2-second socket timeout
        neon_conn = psycopg2.connect(NEON_DATABASE_URL, connect_timeout=2)
        neon_cursor = neon_conn.cursor()

        # Ensure Neon table exists
        neon_cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id UUID PRIMARY KEY,
                laptop_model VARCHAR(255) NOT NULL,
                price NUMERIC(10,2) NOT NULL,
                quantity INTEGER NOT NULL,
                timestamp TIMESTAMP WITH TIME ZONE
            );
        ''')

        synced_ids = []

        for sale in unsynced:
            insert_query = """
                INSERT INTO sales (id, laptop_model, price, quantity, timestamp)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING;
            """
            neon_cursor.execute(insert_query, (
                sale['id'],
                sale['laptop_model'],
                sale['price'],
                sale['quantity'],
                sale['timestamp']
            ))
            synced_ids.append(sale['id'])

        neon_conn.commit()
        neon_cursor.close()

        mark_as_synced(synced_ids)
        print(f"[SYNC SUCCESS] Pushed {len(synced_ids)} transactions to Neon Cloud.")
        return f"Synced {len(synced_ids)} records to Neon Cloud."

    except (psycopg2.OperationalError, psycopg2.DatabaseError) as e:
        print(f"[OFFLINE MODE] Could not reach Neon Cloud: {e}")
        return "Offline mode active. Stored safely in local SQLite database."

    finally:
        if neon_conn:
            neon_conn.close()


if __name__ == "__main__":
    init_db()