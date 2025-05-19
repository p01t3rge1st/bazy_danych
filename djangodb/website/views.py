from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from .models import Student

def home(request):
    all_members = Student.objects.all()
    return render(request, 'home.html', {'all': all_members})

@login_required
def student_panel(request):
    # Sprawdź, czy użytkownik jest studentem (czy istnieje Student z takim username)
    try:
        student = Student.objects.get(student_index=request.user.username)
    except Student.DoesNotExist:
        # Jeśli nie jest studentem, przekieruj np. na stronę główną lub admina
        return redirect('/')
    return render(request, 'student_panel.html', {'student': student})

def custom_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.is_superuser or user.is_staff:
                return redirect('/admin/')
            else:
                return redirect('/panel/')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})
