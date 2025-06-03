from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from .models import Student, Class, Building, Reservation, ReservationStatus, Lecturer, Room, Subject
from django.db.models import Q
from .scripts.pdf_dpwnloader import Pdf_menager
import datetime

def home(request):
    all_members = Student.objects.all()
    return render(request, 'home.html', {'all': all_members})

def remove_old_reservations():
    now = datetime.datetime.now().time()
    today = datetime.date.today()
    old_classes = Class.objects.filter(
        day_of_week=get_day_short(today.weekday())
    ).filter(
        end_time__lt=now.strftime("%H:%M")
    )

    for c in old_classes:
        Reservation.objects.filter(class_field=c).delete()

def get_day_short(weekday):
    days = ['pon', 'wt', 'sr', 'czw', 'pt']
    return days[weekday] if 0 <= weekday <= 4 else None

@login_required
def student_panel(request):
    remove_old_reservations()

    try:
        student = Student.objects.get(student_index=request.user.username)
    except Student.DoesNotExist:
        return redirect('/')

    message = None

    waiting_reservations = Reservation.objects.filter(
        student_index=student,
        status__status_name="Oczekujący"
    )

    #przenoszenie z list oczekujących do zapisanych
    for res in waiting_reservations:
        if res.class_field.max_capacity > res.class_field.enrolled_count:
            message = f"Zostałeś przeniesiony z listy oczekujących do zapisanych na zajęcia {res.class_field}."
            move_from_waiting_list(res.class_field)

    # Obsługa zapisów i wypisów
    if request.method == 'POST':
        class_id = request.POST.get('class_id')
        action = request.POST.get('action')
        if class_id and action:
            class_obj = Class.objects.get(class_id=class_id)
            if action == 'enroll':
                # Sprawdzenie kolizji godzin i dnia
                student_classes = Class.objects.filter(
                    reservation__student_index=student,
                    day_of_week=class_obj.day_of_week
                )

                already_reserved = Reservation.objects.filter(
                    student_index=student,
                    class_field=class_obj
                ).exists()
                if already_reserved:
                    message = "Jesteś już zapisany lub oczekujesz na te zajęcia."

                def time_overlap(start1, end1, start2, end2):
                    return start1 < end2 and end1 > start2

                overlap = False
                for c in student_classes:
                    if time_overlap(
                        class_obj.start_time, class_obj.end_time,
                        c.start_time, c.end_time
                    ) and c.is_cancelled != 1:
                        overlap = True
                        break

                if overlap:
                    message = "Masz już zajęcia w tym dniu w kolidujących godzinach!"
                else:
                    enrolled_count = Reservation.objects.filter(
                        class_field=class_obj,
                        status__status_name="Zapisany"
                    ).count()
                    if enrolled_count < class_obj.max_capacity:
                        status = ReservationStatus.objects.get(status_name="Zapisany")
                        Reservation.objects.create(
                            student_index=student,
                            class_field=class_obj,
                            reservation_date=datetime.date.today(),
                            status=status,
                            note=f"Rezerwacja {student.student_index}-{class_obj.class_id}"
                        )
                        message = "Zostałeś zapisany na zajęcia."
                    else:
                        status = ReservationStatus.objects.get(status_name="Oczekujący")
                        Reservation.objects.create(
                            student_index=student,
                            class_field=class_obj,
                            reservation_date=datetime.date.today(),
                            status=status,
                            note=f"Oczekujący {student.student_index}-{class_obj.class_id}"
                        )
                        message = "Lista jest pełna. Zostałeś dodany do listy oczekujących."

            elif action == 'unenroll':
                        Reservation.objects.filter(
                            student_index=student,
                            class_field=class_obj
                        ).delete()
                        move_from_waiting_list(class_obj)
                        message = "Zostałeś wypisany z zajęć."
    # Zajęcia, na które student jest zapisany
    reserved_classes = Class.objects.filter(reservation__student_index=student)
    # Wszystkie zajęcia, na które NIE jest zapisany
    available_classes = Class.objects.exclude(reservation__student_index=student)
    
    user_reservations_qs = Reservation.objects.filter(student_index=student)

    # Słownik: class_id -> rezerwacja, gdzie Zapisany > Oczekujący
    user_reservations = {}
    for r in user_reservations_qs.order_by('-status__status_name'):
        user_reservations[r.class_field_id] = r

    # Lista unikalnych klas
    reserved_classes = Class.objects.filter(class_id__in=user_reservations.keys())

    

    return render(request, 'student_panel.html', {
        'student': student,
        'reserved_classes': reserved_classes,
        'available_classes': available_classes,
        'message': message,  # Przekaż komunikat do szablonu
        'user_reservations': user_reservations,
    })

def custom_login(request):
    import_classes_from_pdf()
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

@login_required
def class_detail(request, class_id):
    try:
        student = Student.objects.get(student_index=request.user.username)
    except Student.DoesNotExist:
        return redirect('/')

    class_obj = get_object_or_404(Class, class_id=class_id)

    # Czy student jest zapisany?
    is_enrolled = Reservation.objects.filter(
        student_index=student,
        class_field=class_obj,
        status__status_name="Zapisany"
    ).exists()

    # Lista zapisanych studentów
    enrolled_reservations = Reservation.objects.filter(
        class_field=class_obj,
        status__status_name="Zapisany"
    )
    enrolled_count = enrolled_reservations.count()

    participants = []
    if is_enrolled:
        participants = [
            {
                "full_name": f"{r.student_index.first_name} {r.student_index.last_name}",
                "index": r.student_index.student_index
            } for r in enrolled_reservations
        ]

    room = class_obj.room  # zamiast class_obj.room_id
    building = room.building if hasattr(room, 'building') else None
    address = building.address if building else None

    context = {
        'class_obj': class_obj,
        'enrolled_count': enrolled_count,
        'is_enrolled': is_enrolled,
        'participants': participants,
        'lecturer': class_obj.lecturer,
        'room': room,
        'building': building,
        'address': address,
        'day_of_week': class_obj.get_day_of_week_display(),
        'start_time': class_obj.start_time,
        'end_time': class_obj.end_time,
    }

    return render(request, 'class_detail.html', context)



_import_done = False

def import_classes_from_pdf():
    global _import_done
    if _import_done:
        return
    data = Pdf_menager.run()
    for entry in data:
        room_str = entry["room"]
        building_str = entry["building"]
        # Wyciągnij dwie ostatnie cyfry z napisu sali
        room_digits = ''.join(filter(str.isdigit, room_str))
        room_id_str = room_digits[-2:] if len(room_digits) >= 2 else room_digits
        if not room_id_str:
            continue  # pomiń, jeśli nie ma cyfr w numerze sali
        room_id = int(room_id_str)
        # Utwórz lub pobierz budynek
        building, _ = Building.objects.get_or_create(building_id=building_str)
        # Utwórz lub pobierz salę z powiązaniem do budynku
        room, _ = Room.objects.get_or_create(room_id=room_id, building=building)
        instructor = entry["instructor"].strip()
        instructor_parts = instructor.split()
        if len(instructor_parts) > 1:
            first_name = instructor_parts[0]
            last_name = " ".join(instructor_parts[1:])
        else:
            first_name = ""
            last_name = instructor

        lecturer, _ = Lecturer.objects.get_or_create(
            first_name=first_name,
            last_name=last_name
)
        subject, _ = Subject.objects.get_or_create(subject_name=entry["discipline"])
        time_range = entry["time"].split('-')
        if len(time_range) < 2 or not time_range[0].strip() or not time_range[1].strip():
            continue  # pomiń, jeśli nie ma poprawnych godzin
        start_time = time_range[0].strip()
        end_time = time_range[1].strip()
        Class.objects.get_or_create(
            day_of_week=entry["day"].lower()[:3],
            start_time=start_time,
            end_time=end_time,
            room=room,
            lecturer=lecturer,
            subject=subject,
            defaults={
                "max_capacity": 30,
                "enrolled_count": 0,
                "is_cancelled": 0,
                "waiting_list_count": 0,
            }
        )
    _import_done = True

def move_from_waiting_list(class_obj):
    waiting = Reservation.objects.filter(
        class_field=class_obj,
        status__status_name="Oczekujący"
    ).order_by('reservation_date')
    if waiting.exists():
        first = waiting.first()
        student = first.student_index

        # Sprawdź kolizję godzin i dnia
        student_classes = Class.objects.filter(
            reservation__student_index=student,
            day_of_week=class_obj.day_of_week,
            reservation__status__status_name="Zapisany"
        ).exclude(pk=class_obj.pk)

        def time_overlap(start1, end1, start2, end2):
            return start1 < end2 and end1 > start2

        overlap = False
        for c in student_classes:
            if time_overlap(
                class_obj.start_time, class_obj.end_time,
                c.start_time, c.end_time
            ) and c.is_cancelled != 1:
                overlap = True
                break

        if not overlap:
            status = ReservationStatus.objects.get(status_name="Zapisany")
            # Usuń inne rezerwacje tego studenta do tych zajęć (na wszelki wypadek)
            Reservation.objects.filter(
                student_index=first.student_index,
                class_field=class_obj
            ).exclude(pk=first.pk).delete()
            first.status = status
            first.save()