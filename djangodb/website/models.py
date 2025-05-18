# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Building(models.Model):
    building_id = models.TextField(db_column='Building_ID', primary_key=True, blank=True, null=False)  # Field name made lowercase.
    address = models.TextField(db_column='Address')  # Field name made lowercase.

    def __str__(self):
        return f"[{self.building_id}] {self.address}"

    class Meta:
        managed = False
        db_table = 'Building'


class Class(models.Model):
    class_id = models.AutoField(db_column='Class_ID', primary_key=True, blank=True, null=False)  # Field name made lowercase.
    lecturer = models.ForeignKey('Lecturer', models.DO_NOTHING, db_column='Lecturer_ID')  # Field name made lowercase.
    start_time = models.TextField(db_column='Start_Time')  # Field name made lowercase.
    end_time = models.TextField(db_column='End_Time')  # Field name made lowercase.
    max_capacity = models.IntegerField(db_column='Max_Capacity')  # Field name made lowercase.
    enrolled_count = models.IntegerField(db_column='Enrolled_Count')  # Field name made lowercase.
    is_cancelled = models.IntegerField(db_column='Is_Cancelled', blank=True, null=True)  # Field name made lowercase.
    subject = models.ForeignKey('Subject', models.DO_NOTHING, db_column='Subject_ID')  # Field name made lowercase.
    waiting_list_count = models.IntegerField(db_column='Waiting_List_Count', blank=True, null=True)  # Field name made lowercase.
    room = models.ForeignKey('Room', models.DO_NOTHING, db_column='Room_ID')  # Field name made lowercase.

    def __str__(self):
        return f"[{self.class_id}] {self.subject}: {self.start_time}-{self.end_time}"

    class Meta:
        managed = False
        db_table = 'Class'


class Lecturer(models.Model):
    lecturer_id = models.AutoField(db_column='Lecturer_ID', primary_key=True, blank=True, null=False)  # Field name made lowercase.
    first_name = models.TextField(db_column='First_Name')  # Field name made lowercase.
    last_name = models.TextField(db_column='Last_Name')  # Field name made lowercase.
    email = models.TextField(db_column='Email')  # Field name made lowercase.

    def __str__(self):
        return f"[{self.lecturer_id}] {self.first_name} {self.last_name}"

    class Meta:
        managed = False
        db_table = 'Lecturer'


class Reservation(models.Model):
    student_index = models.ForeignKey('Student', models.DO_NOTHING, db_column='Student_Index')  # Field name made lowercase.
    class_field = models.ForeignKey(Class, models.DO_NOTHING, db_column='Class_ID')  # Field name made lowercase. Field renamed because it was a Python reserved word.
    reservation_date = models.TextField(db_column='Reservation_Date')  # Field name made lowercase.
    status = models.ForeignKey('ReservationStatus', models.DO_NOTHING, db_column='Status_ID')  # Field name made lowercase.
    note = models.TextField(db_column='Note', primary_key=True)  # Field name made lowercase.

    def __str__(self):
        return f"{self.student_index} {self.reservation_date} {self.class_field}"

    class Meta:
        managed = False
        db_table = 'Reservation'


class ReservationStatus(models.Model):
    status_id = models.AutoField(db_column='Status_ID', primary_key=True, blank=True, null=False)  # Field name made lowercase.
    status_name = models.TextField(db_column='Status_Name')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Reservation_Status'


class Room(models.Model):
    room_id = models.AutoField(db_column='Room_ID', primary_key=True, blank=True, null=False)  # Field name made lowercase.
    building = models.ForeignKey(Building, models.DO_NOTHING, db_column='Building_ID')  # Field name made lowercase.

    def __str__(self):
        return f"[{self.room_id}] {self.building}"

    class Meta:
        managed = False
        db_table = 'Room'


class Student(models.Model):
    student_index = models.AutoField(db_column='Student_Index', primary_key=True, blank=True, null=False)  # Field name made lowercase.
    first_name = models.TextField(db_column='First_Name')  # Field name made lowercase.
    last_name = models.TextField(db_column='Last_Name')  # Field name made lowercase.
    major = models.TextField(db_column='Major')  # Field name made lowercase.
    department = models.TextField(db_column='Department')  # Field name made lowercase.
    year_of_study = models.IntegerField(db_column='Year_of_Study')  # Field name made lowercase.

    def __str__(self):
        return f"[{self.student_index}] {self.first_name} {self.last_name}"

    class Meta:
        managed = False
        db_table = 'Student'


class Subject(models.Model):
    subject_id = models.AutoField(db_column='Subject_ID', primary_key=True, blank=True, null=False)  # Field name made lowercase.
    subject_name = models.TextField(db_column='Subject_Name')  # Field name made lowercase.

    def __str__(self):
        return f"{self.subject_name}"

    class Meta:
        managed = False
        db_table = 'Subject'
