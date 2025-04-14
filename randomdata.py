import random
from faker import Faker
from db_menager import dbMenager

fake = Faker()
db = dbMenager()
db.create_tables()

def reset_database():
    db.connection.execute("DELETE FROM Reservation")
    db.connection.execute("DELETE FROM Class")
    db.connection.execute("DELETE FROM WaitingList")
    db.connection.execute("DELETE FROM Student")
    db.connection.execute("DELETE FROM Room")
    db.connection.execute("DELETE FROM Building")
    db.connection.execute("DELETE FROM Lecturer")
    db.connection.execute("DELETE FROM Subject")
    db.connection.execute("DELETE FROM Reservation_Status")
    db.connection.commit()

def fill_basic_data():
    buildings = [("B1", "Wittiga"), ("B2", "Grunwaldzka"), ("B3", "Norwida")]
    for b_id, address in buildings:
        db.addBuildingToDatabase(f"{b_id} {address}")
    
    for i in range(1, 6):
        db.addLecturerToDatabase(f"{i} {fake.first_name()} {fake.last_name()} {fake.email()}")

    for i in range(1, 6):
        db.addSubjectToDatabase(f"{i} {fake.word().capitalize()}")

    for i in range(101, 106):
        building = random.choice(buildings)[0]
        db.addRoomToDatabase(f"{i} {building}")
    
    for i in range(1000, 1010):
        db.exportStudentToDatabase(f"{i} {fake.first_name()} {fake.last_name()} Informatyka WIEA {random.randint(1, 5)}")

    status_names = ["Zapisany", "Oczekujący", "Anulowany"]
    for i, name in enumerate(status_names, start=1):
        db.connection.execute("INSERT INTO Reservation_Status(Status_ID, Status_Name) VALUES (?, ?)", (i, name))
    db.connection.commit()

def generate_classes_and_reservations():
    used_slots = set()

    # Tworzenie zajęć
    for _ in range(20):  # 20 zajęć
        start_hour = random.randint(8, 16)
        start_time = f"{start_hour:02d}:00"
        end_time = f"{start_hour+1:02d}:30"

        slot = (start_time, end_time)
        if slot in used_slots:
            continue
        used_slots.add(slot)

        lecturer_id = random.randint(1, 5)
        subject_id = random.randint(1, 5)
        room_id = random.randint(101, 105)
        is_cancelled = random.choice([0, 1])
        waiting_count = random.randint(0, 5)

        db.connection.execute(
            "INSERT INTO Class(Lecturer_ID, Start_Time, End_Time, Is_Cancelled, Subject_ID, Waiting_List_Count, Room_ID) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (lecturer_id, start_time, end_time, is_cancelled, subject_id, waiting_count, room_id)
        )

    db.connection.commit()

    # 🧠 Pobierz poprawne Class_ID
    class_ids = db.connection.execute("SELECT Class_ID FROM Class").fetchall()
    student_ids = db.connection.execute("SELECT Student_Index FROM Student").fetchall()

    # Dodaj rezerwacje
    for class_row in class_ids:
        class_id = class_row[0]
        selected_students = random.sample(student_ids, k=random.randint(1, min(5, len(student_ids))))
        for student_row in selected_students:
            student_id = student_row[0]
            date = fake.date_between(start_date='-30d', end_date='today')
            status = random.randint(1, 3)
            note = fake.word()
            try:
                db.connection.execute(
                    "INSERT INTO Reservation(Student_Index, Class_ID, Reservation_Date, Status_ID, Note) VALUES (?, ?, ?, ?, ?)",
                    (student_id, class_id, str(date), status, note)
                )
            except:
                continue

    db.connection.commit()

if __name__ == "__main__":
    reset_database()
    fill_basic_data()
    generate_classes_and_reservations()
    db.create_view()
    db.close()
