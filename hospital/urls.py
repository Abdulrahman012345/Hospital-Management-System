from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    # Doctors
    path('doctors/', views.doctor_list, name='doctor_list'),
    path('doctors/new/', views.doctor_create, name='doctor_create'),
    path('doctors/<int:pk>/', views.doctor_detail, name='doctor_detail'),
    path('doctors/<int:pk>/edit/', views.doctor_edit, name='doctor_edit'),
    path('doctors/<int:pk>/delete/', views.doctor_delete, name='doctor_delete'),
    # Patients
    path('patients/', views.patient_list, name='patient_list'),
    path('patients/new/', views.patient_create, name='patient_create'),
    path('patients/<int:pk>/', views.patient_detail, name='patient_detail'),
    path('patients/<int:pk>/edit/', views.patient_edit, name='patient_edit'),
    path('patients/<int:pk>/delete/', views.patient_delete, name='patient_delete'),
    # Appointments
    path('appointments/', views.appointment_list, name='appointment_list'),
    path('appointments/new/', views.appointment_create, name='appointment_create'),
    path('appointments/<int:pk>/', views.appointment_detail, name='appointment_detail'),
    path('appointments/<int:pk>/edit/', views.appointment_edit, name='appointment_edit'),
    path('appointments/<int:pk>/delete/', views.appointment_delete, name='appointment_delete'),
    # Bills
    path('billing/', views.bill_list, name='bill_list'),
    path('billing/new/', views.bill_create, name='bill_create'),
    path('billing/<int:pk>/edit/', views.bill_edit, name='bill_edit'),
    path('billing/<int:pk>/delete/', views.bill_delete, name='bill_delete'),
    path('ajax/load-appointments/', views.load_appointments, name='ajax_load_appointments'),
    path('bill/<int:pk>/pay/', views.bill_pay, name='bill_pay'),
    # Prescriptions
    path('prescriptions/<int:pk>/delete/', views.prescription_delete, name='prescription_delete'),
    
    path('change-password/', views.change_password_view, name='change_password')
    
]
