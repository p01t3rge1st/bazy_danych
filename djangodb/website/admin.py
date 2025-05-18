from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Student)
admin.site.register(Building)
admin.site.register(Room)
admin.site.register(Lecturer)
admin.site.register(Class)
admin.site.register(Reservation)
admin.site.register(ReservationStatus)
admin.site.register(Subject)
