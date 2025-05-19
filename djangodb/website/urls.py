from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # strona główna
    path('login/', views.custom_login, name='login'),  # logowanie pod /login/
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
    path('panel/', views.student_panel, name='student_panel'),
    path('lecturer/', views.lecturer_panel, name='lecturer_panel'),  # nowy panel
]

