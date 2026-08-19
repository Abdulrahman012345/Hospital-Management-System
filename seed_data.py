"""
Run: python seed_data.py
Creates demo data + 3 login accounts:
  admin   / admin123
  doctor  / doctor123
  patient / patient123
"""
import os, sys, django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hms_project.settings')
django.setup()

from datetime import date, timedelta, time
from hospital.models import User, Doctor, Patient, Appointment, Prescription, Bill

print("🗑  Clearing existing data...")
Bill.objects.all().delete()
Prescription.objects.all().delete()
Appointment.objects.all().delete()
Patient.objects.all().delete()
Doctor.objects.all().delete()
User.objects.filter(username__in=['admin','doctor','patient','drsmith','drjones','drpatel','alice','bob']).delete()

print("👤 Creating users...")

admin_user = User.objects.create_superuser(
    username='admin', password='admin123',
    first_name='Admin', last_name='User',
    email='admin@medicare.com', role='admin'
)

doc_user = User.objects.create_user(
    username='doctor', password='doctor123',
    first_name='Arun', last_name='Kumar',
    email='doctor@medicare.com', role='doctor'
)

pat_user = User.objects.create_user(
    username='patient', password='patient123',
    first_name='Priya', last_name='Sharma',
    email='patient@medicare.com', role='patient'
)

print("🩺 Creating doctors...")

doctors_data = [
    dict(name='Arun Kumar', specialization='Cardiology', contact='9876543210', email='arun@medicare.com', experience_years=12, available_days='Mon-Fri', user=doc_user),
    dict(name='Meena Iyer', specialization='Neurology', contact='9876543211', email='meena@medicare.com', experience_years=9, available_days='Mon-Wed-Fri'),
    dict(name='Rajesh Patel', specialization='Orthopedics', contact='9876543212', email='rajesh@medicare.com', experience_years=15, available_days='Tue-Thu-Sat'),
    dict(name='Sunita Rao', specialization='Pediatrics', contact='9876543213', email='sunita@medicare.com', experience_years=7, available_days='Mon-Fri'),
    dict(name='Vikram Singh', specialization='General Medicine', contact='9876543214', email='vikram@medicare.com', experience_years=20, available_days='Mon-Sat'),
    dict(name='Deepa Nair', specialization='Dermatology', contact='9876543215', email='deepa@medicare.com', experience_years=6, available_days='Mon-Thu'),
]
doctors = [Doctor.objects.create(**d) for d in doctors_data]

print("🧑 Creating patients...")

patients_data = [
    dict(name='Priya Sharma', age=28, gender='Female', contact='9123456780', email='priya@gmail.com', blood_group='B+', emergency_contact='9123456781', user=pat_user),
    dict(name='Arjun Mehta', age=45, gender='Male', contact='9123456781', email='arjun@gmail.com', blood_group='O+', emergency_contact='9123456782'),
    dict(name='Kavya Reddy', age=32, gender='Female', contact='9123456782', blood_group='A+'),
    dict(name='Suresh Babu', age=60, gender='Male', contact='9123456783', blood_group='AB-', emergency_contact='9123456784'),
    dict(name='Nisha Thomas', age=24, gender='Female', contact='9123456784', blood_group='O-'),
    dict(name='Ramesh Gupta', age=52, gender='Male', contact='9123456785', blood_group='B-'),
    dict(name='Ananya Krishnan', age=19, gender='Female', contact='9123456786', blood_group='A-'),
    dict(name='Mohammed Ali', age=38, gender='Male', contact='9123456787', blood_group='O+'),
]
patients = [Patient.objects.create(**p) for p in patients_data]

today = date.today()

print("📅 Creating appointments...")

appts_data = [
    dict(patient=patients[0], doctor=doctors[0], appointment_date=today, appointment_time=time(9,0), status='Scheduled', reason='Chest pain follow-up'),
    dict(patient=patients[1], doctor=doctors[0], appointment_date=today, appointment_time=time(10,30), status='Pending', reason='Routine cardiac check'),
    dict(patient=patients[2], doctor=doctors[1], appointment_date=today, appointment_time=time(11,0), status='Completed', reason='Migraine treatment', notes='Prescribed topiramate'),
    dict(patient=patients[3], doctor=doctors[2], appointment_date=today - timedelta(days=2), appointment_time=time(9,30), status='Completed', reason='Knee pain'),
    dict(patient=patients[4], doctor=doctors[3], appointment_date=today + timedelta(days=1), appointment_time=time(14,0), status='Scheduled', reason='Child vaccination'),
    dict(patient=patients[5], doctor=doctors[4], appointment_date=today + timedelta(days=2), appointment_time=time(10,0), status='Pending', reason='Diabetes management'),
    dict(patient=patients[6], doctor=doctors[5], appointment_date=today - timedelta(days=5), appointment_time=time(16,0), status='Completed', reason='Skin rash'),
    dict(patient=patients[7], doctor=doctors[4], appointment_date=today - timedelta(days=1), appointment_time=time(9,0), status='Cancelled', reason='General checkup'),
    dict(patient=patients[0], doctor=doctors[1], appointment_date=today - timedelta(days=10), appointment_time=time(11,0), status='Completed', reason='Headache'),
    dict(patient=patients[1], doctor=doctors[2], appointment_date=today + timedelta(days=3), appointment_time=time(15,0), status='Scheduled', reason='Post-op review'),
]
appointments = [Appointment.objects.create(**a) for a in appts_data]

print("💊 Creating prescriptions...")

rx_data = [
    dict(appointment=appointments[2], medicine='Topiramate', dosage='25mg once daily', duration='30 days', instructions='Take at bedtime'),
    dict(appointment=appointments[2], medicine='Ibuprofen', dosage='400mg as needed', duration='7 days', instructions='Take with food'),
    dict(appointment=appointments[3], medicine='Diclofenac Gel', dosage='Apply 3 times daily', duration='14 days', instructions='Apply on affected area'),
    dict(appointment=appointments[6], medicine='Clotrimazole Cream', dosage='Apply twice daily', duration='10 days', instructions='Clean area before applying'),
    dict(appointment=appointments[8], medicine='Paracetamol', dosage='500mg three times daily', duration='5 days', instructions='Take after meals'),
]
[Prescription.objects.create(**r) for r in rx_data]

print("💰 Creating bills...")

from datetime import timedelta
bills_data = [
    dict(patient=patients[0], appointment=appointments[0], amount=1500, paid_amount=1500, status='Paid', description='Cardiology consultation'),
    dict(patient=patients[2], appointment=appointments[2], amount=2200, paid_amount=2200, status='Paid', description='Neurology consultation + medicines'),
    dict(patient=patients[3], appointment=appointments[3], amount=3500, paid_amount=1500, due_date=today+timedelta(days=10), status='Partially Paid', description='Orthopedics consultation + X-ray'),
    dict(patient=patients[4], appointment=appointments[4], amount=800, paid_amount=0, due_date=today+timedelta(days=7), status='Pending', description='Pediatrics consultation'),
    dict(patient=patients[5], appointment=appointments[5], amount=1200, paid_amount=0, due_date=today+timedelta(days=5), status='Pending', description='General medicine consultation'),
    dict(patient=patients[6], appointment=appointments[6], amount=1800, paid_amount=1800, status='Paid', description='Dermatology consultation + treatment'),
    dict(patient=patients[1], appointment=appointments[1], amount=1500, paid_amount=0, due_date=today+timedelta(days=14), status='Pending', description='Cardiology consultation'),
    dict(patient=patients[0], appointment=appointments[8], amount=1200, paid_amount=1200, status='Paid', description='Neurology follow-up'),
]
[Bill.objects.create(**b) for b in bills_data]

print()
print("✅ Seed data created successfully!")
print()
print("─" * 40)
print("LOGIN CREDENTIALS")
print("─" * 40)
print("Admin   → admin   / admin123")
print("Doctor  → doctor  / doctor123")
print("Patient → patient / patient123")
print("─" * 40)
print()
print("Run: python manage.py runserver")
print("Open: http://127.0.0.1:8000/")
