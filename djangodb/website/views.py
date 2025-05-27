from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from .models import Student, Class, Reservation, ReservationStatus, Lecturer
from django.db.models import Q

def home(request):
    all_members = Student.objects.all()
    return render(request, 'home.html', {'all': all_members})

@login_required
def student_panel(request):
    try:
        student = Student.objects.get(student_index=request.user.username)
    except Student.DoesNotExist:
        return redirect('/')

    # Obsługa zapisów i wypisów
    if request.method == 'POST':
        class_id = request.POST.get('class_id')
        action = request.POST.get('action')
        if class_id and action:
            class_obj = Class.objects.get(class_id=class_id)
            if action == 'enroll':
                # Status "zapisany" (załóżmy, że status_id=1 to "zapisany")
                status = ReservationStatus.objects.get(status_name="Zapisany")
                Reservation.objects.create(
                    student_index=student,
                    class_field=class_obj,
                    reservation_date="dzisiaj",  # lub datetime.now()
                    status=status,
                    note=f"Rezerwacja {student.student_index}-{class_obj.class_id}"
                )
            elif action == 'unenroll':
                Reservation.objects.filter(
                    student_index=student,
                    class_field=class_obj
                ).delete()

    # Zajęcia, na które student jest zapisany
    reserved_classes = Class.objects.filter(reservation__student_index=student)
    # Wszystkie zajęcia, na które NIE jest zapisany
    available_classes = Class.objects.exclude(reservation__student_index=student)

    return render(request, 'student_panel.html', {
        'student': student,
        'reserved_classes': reserved_classes,
        'available_classes': available_classes,
    })

def custom_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.is_superuser:
                return redirect('/admin/')
            elif user.groups.filter(name="Lecturer").exists() or user.is_staff:
                return redirect('/lecturer/')
            else:
                return redirect('/panel/')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

@login_required
def lecturer_panel(request):
    try:
        lecturer = Lecturer.objects.get(lecturer_id=int(request.user.username))
    except (Lecturer.DoesNotExist, ValueError):
        return redirect('/')

    # Obsługa anulowania/przywracania zajęć
    if request.method == 'POST':
        class_id = request.POST.get('class_id')
        action = request.POST.get('action')
        if class_id and action:
            try:
                class_obj = Class.objects.get(class_id=class_id, lecturer=lecturer)
                if action == 'cancel':
                    class_obj.is_cancelled = 1
                    class_obj.save()
                elif action == 'restore':
                    class_obj.is_cancelled = 0
                    class_obj.save()
            except Class.DoesNotExist:
                pass

    # Zajęcia prowadzącego
    classes = Class.objects.filter(lecturer=lecturer)
    # Studenci zapisani na każde zajęcia
    class_students = []
    for c in classes:
        reservations = Reservation.objects.filter(class_field=c, status__status_name="Zapisany")
        students = [r.student_index for r in reservations]
        class_students.append((c, students))

    # Obsługa wyrzucania studentów z zajęć
    if request.method == 'POST':
        class_id = request.POST.get('class_id')
        student_id = request.POST.get('student_id')
        action = request.POST.get('action')
        if action == 'kick' and class_id and student_id:
            Reservation.objects.filter(
                class_field_id=class_id,
                student_index_id=student_id
            ).delete()

    return render(request, 'lecturer_panel.html', {
        'lecturer': lecturer,
        'class_students': class_students,
    })
