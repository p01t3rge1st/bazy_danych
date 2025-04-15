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

CREATE_RESERVATION_STATUS_TABLE = "CREATE TABLE IF NOT EXISTS Reservation_Status (Status_ID INTEGER PRIMARY KEY, " \
                                                            "Status_Name TEXT NOT NULL)"

CREATE_RESERVATION_TABLE = "CREATE TABLE IF NOT EXISTS Reservation (Student_Index INTEGER NOT NULL, " \
                                                                    "Class_ID INTEGER NOT NULL,  " \
                                                                    "Reservation_Date TEXT NOT NULL, " \
                                                                    "Status_ID INTEGER NOT NULL, " \
                                                                    "Note TEXT NOT NULL," \
                                                                    "FOREIGN KEY(Class_ID) REFERENCES Class(Class_ID)," \
                                                                    "FOREIGN KEY(Student_Index) REFERENCES Student(Student_Index)," \
                                                                    "FOREIGN KEY(Status_ID) REFERENCES Reservation_Status(Status_ID))"

WAITING_LIST_VIEW = "CREATE VIEW IF NOT EXISTS WaitingList AS " \
                    "SELECT * FROM Reservation WHERE Status_ID = 2"

INSERT_CLASSES = "INSERT INTO Class(Lecturer_ID, Start_Time, End_Time, Is_Cancelled, Subject_ID," \
"Waiting_List_Count, Room_ID) VALUES (?, ?,?,?,?,?,?)"

INSERT_STUDENT = "INSERT INTO Student(Student_Index, First_Name, Last_Name, Major, Department, Year_of_Study)" \
                 "VALUES (?,?,?,?,?,?)"

ADD_RESERVATION = "INSERT INTO Reservation(Student_Index, Class_ID, Reservation_Date, Status, Note)" \
                 "VALUES (?,?,?,?,?)"

ADD_ROOM = "INSERT INTO Room(Room_ID, Building_ID) VALUES (?,?)"

ADD_BUILDING = "INSERT INTO Building(Building_ID, Address) VALUES (?,?)"

ADD_LECTURER = "INSERT INTO Lecturer(Lecturer_ID, First_Name, Last_Name, Email) VALUES (?,?,?,?)"

ADD_SUBJECT = "INSERT INTO Subject(Subject_ID, Subject_Name) VALUES (?,?)"

LECTURERS_CLASSES_VIEW = (
    "CREATE VIEW IF NOT EXISTS LecturersClasses AS "
    "SELECT "
    "c.Class_ID, "
    "s.Subject_Name, "
    "l.First_Name || ' ' || l.Last_Name AS Lecturer_Name "
    "FROM Class c "
    "JOIN Subject s ON c.Subject_ID = s.Subject_ID "
    "JOIN Lecturer l ON c.Lecturer_ID = l.Lecturer_ID "
    "LEFT JOIN Reservation res ON res.Class_ID = c.Class_ID "
    "GROUP BY c.Class_ID "
    "ORDER BY l.Last_Name, l.First_Name;"
)

STUDENTS_ON_CLASS = (
    "SELECT " \
    "st.Student_Index, " \
    "st.First_Name, " \
    "st.Last_Name, " \
    "c.Class_ID, " \
    "s.Subject_Name " \
"FROM " \
    "Reservation r " \
"JOIN " 
   "Student st ON r.Student_Index = st.Student_Index " \
"JOIN " \
    "Class c ON r.Class_ID = c.Class_ID " \
"JOIN " \
    "Subject s ON c.Subject_ID = s.Subject_ID " \
"WHERE " \
    "c.Class_ID = :class_id; " \
)
                         
class dbMenager:

    def create_classes_with_student_count_view(self):
        self.connection.execute("""
        CREATE VIEW IF NOT EXISTS ClassesWithStudentCountView AS
        SELECT
            c.Class_ID,
            s.Subject_Name,
            l.First_Name || ' ' || l.Last_Name AS Lecturer_Name,
            r.Room_ID,
            b.Address AS Building_Address,
            COUNT(res.Student_Index) AS Enrolled_Students
        FROM
            Class c
        JOIN Subject s ON c.Subject_ID = s.Subject_ID
        JOIN Lecturer l ON c.Lecturer_ID = l.Lecturer_ID
        JOIN Room r ON c.Room_ID = r.Room_ID
        JOIN Building b ON r.Building_ID = b.Building_ID
        LEFT JOIN Reservation res ON res.Class_ID = c.Class_ID
        GROUP BY c.Class_ID
        ORDER BY c.Class_ID;
        """)
        self.connection.commit()

    def students_on_class(self, class_id):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(STUDENTS_ON_CLASS, {"class_id" : class_id})
            records = cursor.fetchall()
            print(*records, sep='\n')            

    def display_full_data(self):
        query = "SELECT * FROM FullDataView"
        connection = sqlite3.connect('zajecia.db')
        cursor = connection.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        
        for row in rows:
            print(row)  # Możesz przetwarzać dane lub je zapisać w bardziej przejrzysty sposób
        connection.close()

    def create_available_classes_view(self):
        self.connection.execute('''
            CREATE VIEW IF NOT EXISTS AvailableClassesView AS
            SELECT
                c.Class_ID,
                s.Subject_Name,
                l.First_Name AS Lecturer_First_Name,
                l.Last_Name AS Lecturer_Last_Name,
                b.Address AS Building_Address,
                r.Room_ID,
                c.Start_Time,
                c.End_Time,
                res.Reservation_Date
            FROM Class c
            JOIN Lecturer l ON c.Lecturer_ID = l.Lecturer_ID
            JOIN Subject s ON c.Subject_ID = s.Subject_ID
            JOIN Room r ON c.Room_ID = r.Room_ID
            JOIN Building b ON r.Building_ID = b.Building_ID
            LEFT JOIN Reservation res ON c.Class_ID = res.Class_ID
            WHERE c.Is_Cancelled = 0;
        ''')
        self.connection.commit()

    def create_cancelled_classes_view(self):
        self.connection.execute('''
            CREATE VIEW IF NOT EXISTS CancelledClassesView AS
            SELECT
                c.Class_ID,
                s.Subject_Name,
                l.First_Name AS Lecturer_First_Name,
                l.Last_Name AS Lecturer_Last_Name,
                b.Address AS Building_Address,
                r.Room_ID,
                c.Start_Time,
                c.End_Time,
                res.Reservation_Date
            FROM Class c
            JOIN Lecturer l ON c.Lecturer_ID = l.Lecturer_ID
            JOIN Subject s ON c.Subject_ID = s.Subject_ID
            JOIN Room r ON c.Room_ID = r.Room_ID
            JOIN Building b ON r.Building_ID = b.Building_ID
            LEFT JOIN Reservation res ON c.Class_ID = res.Class_ID
            WHERE c.Is_Cancelled = 1;
        ''')
        self.connection.commit()



    def create_full_data_view(self):
        query = """
        CREATE VIEW IF NOT EXISTS FullDataView AS
        SELECT 
            b.Building_ID,
            b.Address AS Building_Address,
            r.Room_ID,
            s.Subject_Name,
            c.Start_Time,
            c.End_Time,
            c.Max_Capacity,
            c.Enrolled_Count,
            c.Is_Cancelled,
            l.Lecturer_ID,
            l.First_Name AS Lecturer_First_Name,
            l.Last_Name AS Lecturer_Last_Name,
            st.Student_Index,
            st.First_Name AS Student_First_Name,
            st.Last_Name AS Student_Last_Name,
            st.Major,
            st.Department,
            st.Year_of_Study,
            res.Reservation_Date,
            res.Status_ID AS Reservation_Status,
            res.Note AS Reservation_Note
        FROM 
            Building b
        JOIN Room r ON b.Building_ID = r.Building_ID
        JOIN Class c ON r.Room_ID = c.Room_ID
        JOIN Subject s ON c.Subject_ID = s.Subject_ID
        JOIN Lecturer l ON c.Lecturer_ID = l.Lecturer_ID
        JOIN Reservation res ON res.Class_ID = c.Class_ID
        JOIN Student st ON res.Student_Index = st.Student_Index;
        """
        connection = sqlite3.connect('zajecia.db')
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
        connection.close()


    def create_view(self):
        query = """
        CREATE VIEW IF NOT EXISTS BuildingSubjectView AS
        SELECT b.Building_ID, b.Address, s.Subject_Name, l.First_Name AS Lecturer_First_Name, l.Last_Name AS Lecturer_Last_Name
        FROM Building b
        JOIN Room r ON b.Building_ID = r.Building_ID
        JOIN Class c ON r.Room_ID = c.Room_ID
        JOIN Subject s ON c.Subject_ID = s.Subject_ID
        JOIN Lecturer l ON c.Lecturer_ID = l.Lecturer_ID;
        """
        connection = sqlite3.connect('zajecia.db')
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
        connection.close()

    def create_available_classes(self):
        with self.connection:
            self.connection.execute(LECTURERS_CLASSES_VIEW)
            self.connection.commit()



    def __init__(self, db_name = "zajecia.db"):
        self.connection = sqlite3.connect(db_name)
    
    def create_tables(self):
        with self.connection:
            self.connection.execute(CREATE_BUILDING_TABLE)
            self.connection.execute(CREATE_CLASS_TABLE)
            self.connection.execute(CREATE_SUBJECT_TABLE)
            self.connection.execute(CREATE_RESERVATION_STATUS_TABLE)
            self.connection.execute(CREATE_LECTURER_TABLE)
            self.connection.execute(CREATE_ROOM_TABLE)
            self.connection.execute(CREATE_STUDENT_TABLE)
            self.connection.execute(CREATE_RESERVATION_TABLE)
            
            

    def close(self):
        self.connection.close()

    def importClassesToDatabase(self, activity : str):
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
    def addReservationToDatabase(self, text : str):
        with self.connection:
            index = text.split()[0]
            classID = text.split()[1]
            reservationDate = text.split()[2]
            status = text.split()[3]
            note = text.split()[4]

            self.connection.execute(ADD_RESERVATION, (index, classID, reservationDate, status, note))
            self.connection.commit()

    def addRoomToDatabase(self, text):
        with self.connection:
            roomID = text.split()[0]
            BuildingID = text.split()[1]

            # Sprawdzenie czy już istnieje
            result = self.connection.execute("SELECT 1 FROM Room WHERE Room_ID = ?", (roomID,)).fetchone()
            if not result:
                self.connection.execute(ADD_ROOM, (roomID, BuildingID))
                self.connection.commit()


    def addBuildingToDatabase(self, text : str):
        with self.connection:
            buildingID = text.split()[0]
            address = text.split()[1]

            self.connection.execute(ADD_BUILDING, (buildingID, address))
            self.connection.commit()

    def addLecturerToDatabase(self, text : str):
        with self.connection:
            lecturerID = text.split()[0]
            firstName = text.split()[1]
            sureName = text.split()[2]
            email = text.split()[3]

            self.connection.execute(ADD_LECTURER, (lecturerID, firstName, sureName, email))
            self.connection.commit()

    def addSubjectToDatabase(self, text : str):
        with self.connection:
            parts = text.split()
            subjectID = parts[0]
            subjectName = " ".join(parts[1:])

            self.connection.execute(ADD_SUBJECT, (subjectID, subjectName))
            self.connection.commit()

    def waitingListView(self):
        with self.connection:
            self.connection.execute(WAITING_LIST_VIEW)
            self.connection.commit()

if __name__ == "__main__":
    db = dbMenager()
    db.create_tables()
    #db.addBuildingToDatabase("23 Wittiga")
    #db.addLecturerToDatabase("1 Jan Kowalski jan.kowalski@example.com")
    #db.addSubjectToDatabase("1 Matematyka")
    #db.addRoomToDatabase("101 1")
    #db.importClassesToDatabase("Zajecia 09:00 10:30")
    # db.create_classes_with_student_count_view()
    # db.create_cancelled_classes_view()
    # db.create_available_classes_view()
    # db.create_full_data_view()
    # db.create_view()
    db.waitingListView()
    db.close()
