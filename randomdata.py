import sqlite3
import random
from faker import Faker

# Tworzenie instancji generatora danych
fake = Faker()

def add_random_data_to_database(db_name='zajecia.db', num_entries=10):
    # Połączenie z bazą danych
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()

    # Dodanie losowych danych do tabel
    for _ in range(num_entries):
        # Dodajemy dane do tabeli Building
        building_id = f'B{random.randint(1, 10)}'
        address = fake.address().replace("\n", " ")  # Faker generuje adres z nową linią
        cursor.execute("INSERT OR IGNORE INTO Building(Building_ID, Address) VALUES (?, ?)", (building_id, address))

        # Dodajemy dane do tabeli Room
        room_id = random.randint(1, 20)
        cursor.execute("INSERT OR IGNORE INTO Room(Room_ID, Building_ID) VALUES (?, ?)", (room_id, building_id))

        # Dodajemy dane do tabeli Lecturer
        lecturer_id = random.randint(1, 10)
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = fake.email()
        cursor.execute("INSERT OR IGNORE INTO Lecturer(Lecturer_ID, First_Name, Last_Name, Email) VALUES (?, ?, ?, ?)", 
                       (lecturer_id, first_name, last_name, email))

        # Dodajemy dane do tabeli Subject
        subject_id = random.randint(1, 10)
        subject_name = fake.job()
        cursor.execute("INSERT OR IGNORE INTO Subject(Subject_ID, Subject_Name) VALUES (?, ?)", 
                       (subject_id, subject_name))

        # Dodajemy dane do tabeli Class
        start_time = fake.time()
        end_time = fake.time()
        max_capacity = random.randint(20, 50)
        enrolled_count = random.randint(0, max_capacity)
        subject_id = random.randint(1, 10)  # Zakładając, że mamy przynajmniej 10 przedmiotów
        room_id = random.randint(1, 20)
        cursor.execute("INSERT OR IGNORE INTO Class(Lecturer_ID, Start_Time, End_Time, Max_Capacity, Enrolled_Count, Subject_ID, Room_ID) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                       (lecturer_id, start_time, end_time, max_capacity, enrolled_count, subject_id, room_id))

    # Zatwierdzenie zmian w bazie danych i zamknięcie połączenia
    connection.commit()
    connection.close()

# Uruchomienie funkcji generującej dane
add_random_data_to_database(db_name='zajecia.db', num_entries=10)

