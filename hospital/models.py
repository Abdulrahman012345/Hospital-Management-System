from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='patient')
    phone = models.CharField(max_length=15, blank=True, null=True)
    # ADD THIS NEW FIELD:
    requires_password_change = models.BooleanField(default=False) 
    def is_admin_user(self):
        return self.role == 'admin'

    def is_doctor_user(self):
        return self.role == 'doctor'

    def is_patient_user(self):
        return self.role == 'patient'


class Doctor(models.Model):
    SPECIALIZATION_CHOICES = [
        ('Cardiology', 'Cardiology'),
        ('Neurology', 'Neurology'),
        ('Orthopedics', 'Orthopedics'),
        ('Pediatrics', 'Pediatrics'),
        ('Dermatology', 'Dermatology'),
        ('General Medicine', 'General Medicine'),
        ('Gynecology', 'Gynecology'),
        ('Ophthalmology', 'Ophthalmology'),
        ('Psychiatry', 'Psychiatry'),
        ('Radiology', 'Radiology'),
        ('Surgery', 'Surgery'),
        ('Urology', 'Urology'),
        ('ENT', 'ENT'),
        ('Oncology', 'Oncology'),
        ('Endocrinology', 'Endocrinology'),
    ]
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='doctor_profile')
    doctor_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100, choices=SPECIALIZATION_CHOICES)
    contact = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    experience_years = models.PositiveIntegerField(default=0)
    available_days = models.CharField(max_length=200, default='Mon-Fri')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Dr. {self.name}"

    @property
    def total_appointments(self):
        return self.appointment_set.count()


class Patient(models.Model):
    GENDER_CHOICES = [('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')]
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-'),
    ]
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='patient_profile')
    patient_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    contact = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES, blank=True, null=True)
    emergency_contact = models.CharField(max_length=15, blank=True, null=True)
    registered_on = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Scheduled', 'Scheduled'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
        ('No-Show', 'No-Show'),
    ]
    appointment_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    appointment_date = models.DateField()
    appointment_time = models.TimeField(default='09:00')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    reason = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"#{self.appointment_id} - {self.patient.name} with {self.doctor.name}"

    class Meta:
        ordering = ['-appointment_date', '-appointment_time']


class Prescription(models.Model):
    prescription_id = models.AutoField(primary_key=True)
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='prescriptions')
    medicine = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100)
    duration = models.CharField(max_length=100, default='7 days')
    instructions = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.medicine} for {self.appointment.patient.name}"


class Bill(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Partially Paid', 'Partially Paid'),
        ('Waived', 'Waived'),
    ]
    bill_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bill_date = models.DateField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Bill #{self.bill_id} - {self.patient.name}"

    @property
    def balance(self):
        return self.amount - self.paid_amount
