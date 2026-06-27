import uuid
import random
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import execute_values
from faker import Faker

HOST = '127.0.0.1'
USER = 'postgres'
PASSWORD = '12345'
DATABASE = 'opt_db'
PORT = '5432'

CLIENTS_COUNT = 10_000
CLASSES_COUNT = 500
VISITS_COUNT = 100_000
CHUNK_SIZE = 10_000

fake = Faker()


def insert_clients(cursor):
    print("Inserting into gym_clients...")
    client_insert_query = "INSERT INTO gym_clients (client_id, full_name, email, membership_type, join_date) VALUES %s"

    client_ids = []
    clients_data = []
    for _ in range(CLIENTS_COUNT):
        c_id = str(uuid.uuid4())
        client_ids.append(c_id)
        clients_data.append((c_id, fake.name(), fake.email(), random.choice(['Basic', 'Standard', 'Premium']), fake.date_between(start_date='-5y', end_date='today')))
    execute_values(cursor, client_insert_query, clients_data)
    return client_ids


def insert_classes(cursor):
    print("Inserting into gym_classes...")
    class_insert_query = "INSERT INTO gym_classes (class_name, trainer_name, class_category) VALUES %s RETURNING class_id"

    classes_data = [(fake.word(), fake.name(), random.choice(['Category1', 'Category2', 'Category3', 'Category4', 'Category5'])) for _ in range(CLASSES_COUNT)]

    execute_values(cursor, class_insert_query, classes_data)
    cursor.execute("SELECT class_id FROM gym_classes")
    return [row[0] for row in cursor.fetchall()]


def insert_visits(cursor, client_ids, class_ids):
    print("Inserting into gym_visits...")
    visit_insert_query = "INSERT INTO gym_visits (visit_date, client_id, class_id) VALUES %s"

    for start in range(0, VISITS_COUNT, CHUNK_SIZE):
        current_chunk = min(CHUNK_SIZE, VISITS_COUNT - start)
        visits_data = [
            (datetime.now() - timedelta(days=random.randint(0, 365)), random.choice(client_ids),
             random.choice(class_ids))
            for _ in range(current_chunk)
        ]
        execute_values(cursor, visit_insert_query, visits_data)
        print(f"Inserted {start + current_chunk} visits into gym_visits...")


def main():
    connection = psycopg2.connect(host=HOST, user=USER, password=PASSWORD, dbname=DATABASE, port=PORT)
    try:
        with connection:
            with connection.cursor() as cursor:
                client_ids = insert_clients(cursor)
                class_ids = insert_classes(cursor)
                insert_visits(cursor, client_ids, class_ids)
    finally:
        connection.close()


if __name__ == "__main__":
    main()