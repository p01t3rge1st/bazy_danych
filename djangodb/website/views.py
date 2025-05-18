from django.shortcuts import render
from .models import Student

def home(request):
    all_members = Student.objects.all()
    return render(request, 'home.html', {'all': all_members})
