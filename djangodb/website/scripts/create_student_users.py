from django.contrib.auth.models import User
from website.models import Student

for student in Student.objects.all():
    username = str(student.student_index)
    if not User.objects.filter(username=username).exists():
        User.objects.create_user(
            username=username,
            password='password',
            first_name=student.first_name,
            last_name=student.last_name
        )