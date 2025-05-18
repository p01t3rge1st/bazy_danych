from django.db import models

# Create your models here.
class Student(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    major = models.CharField(max_length=50)
    department = models.CharField(max_length=50)
    year_of_study = models.IntegerField()

    def __str__(self):
        return self.name + ' ' + self.last_name + ' ' + self.id