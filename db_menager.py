import sqlite3
from bin.pe_activities import PeActivities

CREATE_BUILDING_TABLE  = "CREATE TABLE IF NOT EXISTS Building (Building_ID TEXT PRIMARY KEY, " \
                                                                "Address TEXT NOT NULL)"

CREATE_CLASS_TABLE = "CREATE TABLE IF NOT EXISTS Class (Class_ID INTEGER PRIMARY KEY, " \
                    "Lecturer_ID INTEGER NOT NULL," \
                    "Start_Time TEXT NOT NULL, " \
                    "End_Time TEXT NOT NULL, " \
                    "Max_Capacity INTEGER NOT NULL DEFAULT 20, " \
                    "Enrolled_Count INTEGER NOT NULL DEFAULT 0," \
                    "Is_Cancelled INT, " \
                    "Subject_ID INTEGER NOT NULL," \
                    "Waiting_List_Count INT," \
                    "Room_ID INTEGER NOT NULL," \
                    "FOREIGN KEY(Subject_ID) REFERENCES Subject(Subject_ID)," \
                    "FOREIGN KEY(Lecturer_ID) REFERENCES Lecturer(Lecturer_ID)," \
                    "FOREIGN KEY(Room_ID) REFERENCES Room(Room_ID)," \
                   "UNIQUE(Lecturer_ID, Start_Time, End_Time, Subject_ID, Room_ID) )"

CREATE_LECTURER_TABLE = "CREATE TABLE IF NOT EXISTS Lecturer (Lecturer_ID INTEGER PRIMARY KEY, " \
                                                            "First_Name TEXT NOT NULL," \
                                                            "Last_Name TEXT NOT NULL, " \
                                                            "Email TEXT NOT NULL)"

CREATE_ROOM_TABLE = "CREATE TABLE IF NOT EXISTS Room (Room_ID INTEGER PRIMARY KEY, " \
                                                    "Building_ID TEXT NOT NULL, " \
                                                    "FOREIGN KEY(Building_ID) REFERENCES Building(Building_ID))"

CREATE_STUDENT_TABLE = "CREATE TABLE IF NOT EXISTS Student (Student_Index INTEGER PRIMARY KEY, " \
                                                            "First_Name TEXT NOT NULL, " \
                                                            "Last_Name TEXT NOT NULL, " \
                                                            "Major TEXT NOT NULL, " \
                                                            "Department TEXT NOT NULL," \
                                                            "Year_of_Study INTEGER NOT NULL)"

CREATE_SUBJECT_TABLE = "CREATE TABLE IF NOT EXISTS Subject (Subject_ID INTEGER PRIMARY KEY, " \
                                                            "Subject_Name TEXT NOT NULL)"

CREATE_RESERVATION_TABLE = "CREATE TABLE IF NOT EXISTS Reservation (Student_Index INTEGER NOT NULL, " \
                                                                    "Class_ID INTEGER NOT NULL,  " \
                                                                    "Reservation_Date TEXT NOT NULL, " \
                                                                    "Status TEXT NOT NULL, " \
                                                                    "Note TEXT NOT NULL," \
                                                                    "FOREIGN KEY(Class_ID) REFERENCES Class(Class_ID)," \
                                                                    "FOREIGN KEY(Student_Index) REFERENCES Student(Student_Index))"

CREATE_WAITING_LIST_TABLE = "CREATE TABLE IF NOT EXISTS WaitingList (Waiting_ID INTEGER PRIMARY KEY AUTOINCREMENT," \
                                                                    "Student_Index INTEGER NOT NULL, " \
                                                                    "Class_ID INTEGER NOT NULL, " \
                                                                    "Request_Date TEXT NOT NULL, " \
                                                                    "FOREIGN KEY(Student_Index) REFERENCES Student(Student_Index)," \
                                                                    "FOREIGN KEY(Class_ID) REFERENCES Class(Class_ID))"

INSERT_CLASSES = "INSERT INTO Class(Lecturer_ID, Start_Time, End_Time, Is_Cancelled, Subject_ID," \
"Waiting_List_Count, Room_ID) VALUES (?, ?,?,?,?,?,?)"

INSERT_STUDENT = "INSERT INTO Student(Student_Index, First_Name, Last_Name, Major, Department, Year_of_Study)" \
                 "VALUES (?,?,?,?,?,?)"

ADD_RESERVATION = "INSERT INTO Reservation(Student_Index, Class_ID, Reservation_Date, Status, Note)" \
                 "VALUES (?,?,?,?,?)"

ADD_ROOM = "INSERT INTO Room(Room_ID, Building_ID) VALUES (?,?)"

class dbMenager:

    def __init__(self, db_name = "zajecia.db"):
        self.connection = sqlite3.connect(db_name)
    
    def create_tables(self):
        with self.connection:
            self.connection.execute(CREATE_BUILDING_TABLE)
            self.connection.execute(CREATE_CLASS_TABLE)
            self.connection.execute(CREATE_SUBJECT_TABLE)
            self.connection.execute(CREATE_LECTURER_TABLE)
            self.connection.execute(CREATE_ROOM_TABLE)
            self.connection.execute(CREATE_STUDENT_TABLE)
            self.connection.execute(CREATE_RESERVATION_TABLE)
            self.connection.execute(CREATE_WAITING_LIST_TABLE)
            
            

    def close(self):
        self.connection.close()

    def importClassesFromFile(self, activity : str):
        with self.connection:
            insertedClass = activity.split()
            self.connection.execute(INSERT_CLASSES, (15, insertedClass[1], insertedClass[2],
                                                    0, 2, 5, 6))
            self.connection.commit()
    def exportStudentToDatabase(self, text : str):
        with self.connection:
            index = text.split()[0]
            name = text.split()[1]
            surname = text.split()[2]
            major = text.split()[3]
            department = text.split()[4]
            yearOfStudy = text.split()[5]

            self.connection.execute(INSERT_STUDENT, (index, name, surname, major, department, yearOfStudy))
            self.connection.commit()
    def addReservation(self, text : str):
        with self.connection:
            index = text.split()[0]
            classID = text.split()[1]
            reservationDate = text.split()[2]
            status = text.split()[3]
            note = text.split()[4]

            self.connection.execute(ADD_RESERVATION, (index, classID, reservationDate, status, note))
            self.connection.commit()

    def addRoom(self, text):
        with self.connection:
            roomID = text.split()[0]
            BuildingID = text.split()[1]

            self.connection.execute(ADD_ROOM, (roomID, BuildingID))
            self.connection.commit()

if __name__ == "__main__":
    db = dbMenager()
    db.create_tables()
    db.addRoom("11 23")
    db.close()