from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import date, timedelta
from .models import User, Doctor, Patient, Appointment, Prescription, Bill
from .forms import (DoctorForm, PatientForm, AppointmentForm, PrescriptionForm,
                    BillForm, LoginForm, RegisterForm,PatientAppointmentForm)
from django.http import JsonResponse



# ─── AUTH ────────────────────────────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = LoginForm(request.POST or None)
    
    if request.method == 'POST' and form.is_valid():
        user = authenticate(request,
                            username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])
        if user:
            login(request, user)
            
            # --- NEW INTERCEPTOR CODE ---
            if user.requires_password_change:
                messages.info(request, "Please update your temporary password to continue.")
                return redirect('change_password')
            # ----------------------------
            
            return redirect('dashboard')
        messages.error(request, 'Invalid username or password.')
        
    return render(request, 'hospital/login.html', {'form': form})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = RegisterForm(request.POST or None)
    
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.role = 'patient'
        user.set_password(form.cleaned_data['password'])
        user.save()
        
        # Save ALL the fields to the Patient profile
        Patient.objects.create(
            user=user,
            name=f"{user.first_name} {user.last_name}".strip(),
            email=user.email,
            contact=form.cleaned_data.get('phone', ''),
            age=form.cleaned_data.get('age'),
            gender=form.cleaned_data.get('gender'),
            blood_group=form.cleaned_data.get('blood_group'),
            address=form.cleaned_data.get('address'),
            emergency_contact=form.cleaned_data.get('emergency_contact')
        )
        
        login(request, user)
        messages.success(request, f'Welcome, {user.first_name}! Your profile is fully set up.')
        return redirect('dashboard')
        
    return render(request, 'hospital/register.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


# ─── DASHBOARD ───────────────────────────────────────────────────────────────
@login_required
def change_password_view(request):
    if not request.user.requires_password_change:
        return redirect('dashboard')

    if request.method == 'POST':
        p1 = request.POST.get('new_password')
        p2 = request.POST.get('confirm_password')
        
        if p1 == p2 and len(p1) >= 8:
            request.user.set_password(p1)
            request.user.requires_password_change = False
            request.user.save()
            
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Password updated successfully! Welcome to your dashboard.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Passwords must match and be at least 8 characters long.')

    return render(request, 'hospital/change_password.html')


@login_required
def dashboard(request):
    today = date.today()
    user = request.user
    # --- NEW SECURITY CHECK ---
    if getattr(user, 'requires_password_change', False):
        return redirect('change_password')
    # --------------------------
    if user.role == 'doctor':
        try:
            doctor = user.doctor_profile
            my_appointments = Appointment.objects.filter(doctor=doctor).select_related('patient')
            pending = my_appointments.filter(status='Pending').count()
            scheduled = my_appointments.filter(status='Scheduled').count()
            completed = my_appointments.filter(status='Completed').count()
            today_appts = my_appointments.filter(appointment_date=today)
            upcoming = my_appointments.filter(
                appointment_date__gte=today, status__in=['Pending', 'Scheduled']
            ).order_by('appointment_date', 'appointment_time')[:8]
            context = {
                'role': 'doctor', 'doctor': doctor,
                'pending': pending, 'scheduled': scheduled,
                'completed': completed, 'today_appts': today_appts,
                'upcoming': upcoming,
            }
        except Exception:
            context = {'role': 'doctor', 'error': 'No doctor profile linked to your account.'}

    elif user.role == 'patient':
        try:
            patient = user.patient_profile
            my_appointments = Appointment.objects.filter(patient=patient).select_related('doctor')
            my_bills = Bill.objects.filter(patient=patient)
            total_billed = my_bills.aggregate(Sum('amount'))['amount__sum'] or 0
            total_paid = my_bills.aggregate(Sum('paid_amount'))['paid_amount__sum'] or 0
            upcoming = my_appointments.filter(
                appointment_date__gte=today, status__in=['Pending', 'Scheduled']
            ).order_by('appointment_date')[:5]
            context = {
                'role': 'patient', 'patient': patient,
                'my_appointments': my_appointments[:5],
                'my_bills': my_bills[:5],
                'total_billed': total_billed,
                'total_paid': total_paid,
                'balance_due': total_billed - total_paid,
                'upcoming': upcoming,
            }
        except Exception:
            context = {'role': 'patient', 'error': 'No patient profile linked to your account.'}

    else:  # admin
        total_patients = Patient.objects.count()
        total_doctors = Doctor.objects.count()
        today_appointments = Appointment.objects.filter(appointment_date=today).count()
        total_revenue = Bill.objects.filter(status='Paid').aggregate(Sum('amount'))['amount__sum'] or 0
        pending_bills = Bill.objects.filter(status='Pending').count()
        recent_appointments = Appointment.objects.select_related('patient', 'doctor').order_by('-created_at')[:8]
        upcoming = Appointment.objects.filter(
            appointment_date__gte=today, status__in=['Pending', 'Scheduled']
        ).select_related('patient', 'doctor').order_by('appointment_date', 'appointment_time')[:5]
        recent_patients = Patient.objects.order_by('-registered_on')[:5]
        completed_today = Appointment.objects.filter(appointment_date=today, status='Completed').count()
        pending_appointments = Appointment.objects.filter(status='Pending').count()

        # Monthly revenue (last 6 months)
        monthly_data = []
        for i in range(5, -1, -1):
            month_start = (today.replace(day=1) - timedelta(days=i * 30))
            month_start = month_start.replace(day=1)
            if month_start.month == 12:
                month_end = month_start.replace(year=month_start.year + 1, month=1, day=1)
            else:
                month_end = month_start.replace(month=month_start.month + 1, day=1)
            rev = Bill.objects.filter(
                status='Paid', bill_date__gte=month_start, bill_date__lt=month_end
            ).aggregate(Sum('amount'))['amount__sum'] or 0
            monthly_data.append({'month': month_start.strftime('%b'), 'revenue': float(rev)})

        context = {
            'role': 'admin',
            'total_patients': total_patients,
            'total_doctors': total_doctors,
            'today_appointments': today_appointments,
            'total_revenue': total_revenue,
            'pending_bills': pending_bills,
            'recent_appointments': recent_appointments,
            'upcoming': upcoming,
            'recent_patients': recent_patients,
            'today': today,
            'completed_today': completed_today,
            'pending_appointments': pending_appointments,
            'monthly_data': monthly_data,
        }

    return render(request, 'hospital/dashboard.html', context)


# ─── DOCTOR VIEWS ─────────────────────────────────────────────────────────────

@login_required
def doctor_list(request):
    if request.user.role not in ['admin']:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    q = request.GET.get('q', '')
    spec = request.GET.get('spec', '')
    doctors = Doctor.objects.all()
    if q:
        doctors = doctors.filter(name__icontains=q)
    if spec:
        doctors = doctors.filter(specialization=spec)
    specializations = Doctor.objects.values_list('specialization', flat=True).distinct()
    return render(request, 'hospital/doctor_list.html',
                  {'doctors': doctors, 'q': q, 'specializations': specializations, 'spec': spec})


@login_required
def doctor_detail(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    appointments = doctor.appointment_set.select_related('patient').order_by('-appointment_date')[:10]
    return render(request, 'hospital/doctor_detail.html', {'doctor': doctor, 'appointments': appointments})


@login_required
def doctor_create(request):
    if request.user.role != 'admin':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    form = DoctorForm(request.POST or None)
    
    if form.is_valid():
        doctor = form.save(commit=False)
        
        # 1. Generate Username and Temp Password
        base_name = doctor.name.split()[0].lower()
        username = f"dr_{base_name}_{random.randint(100, 999)}"
        temp_pass = generate_temp_password()
        
        # 2. Create the User Account
        user = User.objects.create(
            username=username,
            email=doctor.email,
            role='doctor',
            requires_password_change=True # Force the reset!
        )
        user.set_password(temp_pass)
        user.save()
        
        # 3. Link user to doctor and save
        doctor.user = user
        doctor.save()
        
        # 4. Show credentials to the Admin (Update this line)
        messages.success(request, f'Username: {username}   |   Password: {temp_pass}', extra_tags='credentials')
        return redirect('doctor_list')
        
    return render(request, 'hospital/form.html',
                  {'form': form, 'title': 'Add New Doctor', 'subtitle': 'Register a new physician', 'icon': 'user-md', 'back_url': 'doctor_list'})
@login_required
def doctor_edit(request, pk):
    if request.user.role != 'admin':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    doctor = get_object_or_404(Doctor, pk=pk)
    form = DoctorForm(request.POST or None, instance=doctor)
    if form.is_valid():
        form.save()
        messages.success(request, 'Doctor updated successfully!')
        return redirect('doctor_list')
    return render(request, 'hospital/form.html',
                  {'form': form, 'title': f'Edit Dr. {doctor.name}', 'subtitle': 'Update physician details', 'icon': 'edit', 'back_url': 'doctor_list'})


@login_required
def doctor_delete(request, pk):
    if request.user.role != 'admin':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    doctor = get_object_or_404(Doctor, pk=pk)
    if request.method == 'POST':
        doctor.delete()
        messages.success(request, 'Doctor removed successfully.')
        return redirect('doctor_list')
    return render(request, 'hospital/confirm_delete.html',
                  {'object': doctor, 'type': 'Doctor', 'back_url': 'doctor_list'})


# ─── PATIENT VIEWS ────────────────────────────────────────────────────────────

@login_required
def patient_list(request):
    if request.user.role not in ['admin', 'doctor']:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    q = request.GET.get('q', '')
    gender = request.GET.get('gender', '')
    patients = Patient.objects.all().order_by('-registered_on')
    if q:
        patients = patients.filter(Q(name__icontains=q) | Q(contact__icontains=q))
    if gender:
        patients = patients.filter(gender=gender)
    return render(request, 'hospital/patient_list.html', {'patients': patients, 'q': q, 'gender': gender})


@login_required
def patient_detail(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    # Patient can only see their own profile
    if request.user.role == 'patient':
        try:
            if request.user.patient_profile.pk != pk:
                messages.error(request, 'Access denied.')
                return redirect('dashboard')
        except Exception:
            pass
    appointments = patient.appointment_set.select_related('doctor').order_by('-appointment_date')
    bills = patient.bill_set.order_by('-bill_date')
    total_billed = bills.aggregate(Sum('amount'))['amount__sum'] or 0
    total_paid = bills.aggregate(Sum('paid_amount'))['paid_amount__sum'] or 0
    return render(request, 'hospital/patient_detail.html', {
        'patient': patient, 'appointments': appointments,
        'bills': bills, 'total_billed': total_billed, 'total_paid': total_paid
    })
@login_required
def patient_create(request):
    if request.user.role != 'admin':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    form = PatientForm(request.POST or None)
    
    if form.is_valid():
        patient = form.save(commit=False)
        
        # 1. Generate Username and Temp Password
        base_name = patient.name.split()[0].lower()
        username = f"pt_{base_name}_{random.randint(100, 999)}"
        temp_pass = generate_temp_password()
        
        # 2. Create the User Account
        user = User.objects.create(
            username=username,
            email=patient.email,
            role='patient',
            requires_password_change=True # Force the reset!
        )
        user.set_password(temp_pass)
        user.save()
        
        # 3. Link user to patient and save
        patient.user = user
        patient.save()
        
        # 4. Show credentials to the Admin (Update this line)
        messages.success(request, f'Username: {username}   |   Password: {temp_pass}', extra_tags='credentials')
        return redirect('patient_list')
        
    return render(request, 'hospital/form.html',
                  {'form': form, 'title': 'Register New Patient', 'subtitle': 'Add a new patient record', 'icon': 'user-plus', 'back_url': 'patient_list'})
@login_required
def patient_edit(request, pk):
    if request.user.role != 'admin':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    patient = get_object_or_404(Patient, pk=pk)
    form = PatientForm(request.POST or None, instance=patient)
    if form.is_valid():
        form.save()
        messages.success(request, 'Patient updated successfully!')
        return redirect('patient_list')
    return render(request, 'hospital/form.html',
                  {'form': form, 'title': f'Edit {patient.name}', 'subtitle': 'Update patient information', 'icon': 'edit', 'back_url': 'patient_list'})


@login_required
def patient_delete(request, pk):
    if request.user.role != 'admin':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        patient.delete()
        messages.success(request, 'Patient record removed.')
        return redirect('patient_list')
    return render(request, 'hospital/confirm_delete.html',
                  {'object': patient, 'type': 'Patient', 'back_url': 'patient_list'})


# ─── APPOINTMENT VIEWS ────────────────────────────────────────────────────────

@login_required
def appointment_list(request):
    status = request.GET.get('status', '')
    date_filter = request.GET.get('date', '')
    user = request.user

    if user.role == 'doctor':
        try:
            appointments = Appointment.objects.filter(doctor=user.doctor_profile).select_related('patient', 'doctor')
        except Exception:
            appointments = Appointment.objects.none()
    elif user.role == 'patient':
        try:
            appointments = Appointment.objects.filter(patient=user.patient_profile).select_related('patient', 'doctor')
        except Exception:
            appointments = Appointment.objects.none()
    else:
        appointments = Appointment.objects.select_related('patient', 'doctor')

    appointments = appointments.order_by('-appointment_date', '-appointment_time')
    if status:
        appointments = appointments.filter(status=status)
    if date_filter:
        appointments = appointments.filter(appointment_date=date_filter)
    return render(request, 'hospital/appointment_list.html',
                  {'appointments': appointments, 'status': status, 'date_filter': date_filter})


@login_required
def appointment_detail(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    prescriptions = appointment.prescriptions.all()
    form = PrescriptionForm()

    if request.method == 'POST':
        action = request.POST.get('action')
        # Status change by doctor/admin
        if action in ['accept', 'reject', 'complete'] and request.user.role in ['doctor', 'admin']:
            status_map = {'accept': 'Scheduled', 'reject': 'Cancelled', 'complete': 'Completed'}
            appointment.status = status_map[action]
            appointment.save()
            messages.success(request, f'Appointment marked as {appointment.status}.')
            return redirect('appointment_detail', pk=pk)
        # Add prescription
        form = PrescriptionForm(request.POST)
        if form.is_valid():
            p = form.save(commit=False)
            p.appointment = appointment
            p.save()
            messages.success(request, 'Prescription added!')
            return redirect('appointment_detail', pk=pk)

    return render(request, 'hospital/appointment_detail.html', {
        'appointment': appointment, 'prescriptions': prescriptions, 'form': form
    })


@login_required
def appointment_create(request):
    user = request.user
    
    # 1. Select the correct form based on the user's role
    if user.role == 'patient':
        form_class = PatientAppointmentForm
    else:
        form_class = AppointmentForm

    form = form_class(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        # Pause the save to attach hidden data
        appointment = form.save(commit=False)
        
        # 2. Auto-fill the restricted fields for patients
        if user.role == 'patient':
            try:
                appointment.patient = user.patient_profile
                appointment.status = 'Pending' # Enforce security so they can't tamper with status
            except Exception:
                messages.error(request, 'No patient profile linked to this account.')
                return redirect('dashboard')
                
        # 3. Commit to the database
        appointment.save()
        messages.success(request, 'Appointment booked successfully!')
        return redirect('appointment_list')
        
    # Set dynamic titles based on who is viewing the page
    title = 'Book Appointment'
    subtitle = 'Schedule a consultation with our doctors' if user.role == 'patient' else 'Schedule a new appointment'

    return render(request, 'hospital/form.html', {
        'form': form, 
        'title': title, 
        'subtitle': subtitle, 
        'icon': 'calendar-plus', 
        'back_url': 'appointment_list'
    })

@login_required
def appointment_edit(request, pk):
    if request.user.role == 'patient':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    appointment = get_object_or_404(Appointment, pk=pk)
    form = AppointmentForm(request.POST or None, instance=appointment)
    if form.is_valid():
        form.save()
        messages.success(request, 'Appointment updated!')
        return redirect('appointment_list')
    return render(request, 'hospital/form.html',
                  {'form': form, 'title': 'Edit Appointment', 'subtitle': 'Update appointment details', 'icon': 'edit', 'back_url': 'appointment_list'})


@login_required
def appointment_delete(request, pk):
    if request.user.role not in ['admin']:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        appointment.delete()
        messages.success(request, 'Appointment cancelled.')
        return redirect('appointment_list')
    return render(request, 'hospital/confirm_delete.html',
                  {'object': appointment, 'type': 'Appointment', 'back_url': 'appointment_list'})


# ─── BILLING VIEWS ────────────────────────────────────────────────────────────

@login_required
def bill_list(request):
    status = request.GET.get('status', '')
    user = request.user

    if user.role == 'patient':
        try:
            bills = Bill.objects.filter(patient=user.patient_profile).select_related('patient')
        except Exception:
            bills = Bill.objects.none()
    else:
        bills = Bill.objects.select_related('patient').order_by('-bill_date')

    if status:
        bills = bills.filter(status=status)

    total_revenue = Bill.objects.filter(status='Paid').aggregate(Sum('amount'))['amount__sum'] or 0
    pending_amount = Bill.objects.filter(status='Pending').aggregate(Sum('amount'))['amount__sum'] or 0
    return render(request, 'hospital/bill_list.html', {
        'bills': bills, 'status': status,
        'total_revenue': total_revenue, 'pending_amount': pending_amount
    })


@login_required
def load_appointments(request):
    patient_id = request.GET.get('patient_id')
    
    # If no patient is selected, return an empty list
    if not patient_id:
        return JsonResponse([], safe=False)
        
    # Get appointments for this patient
    appointments = Appointment.objects.filter(patient_id=patient_id).order_by('-appointment_date')
    
    # Format the data into a list of dictionaries for JavaScript to read
    appointment_data = []
    for appt in appointments:
        appointment_data.append({
            'id': appt.appointment_id,
            'text': f"#{appt.appointment_id} - {appt.appointment_date} ({appt.status})"
        })
        
    return JsonResponse(appointment_data, safe=False)
@login_required
def bill_create(request):
    if request.user.role != 'admin':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    form = BillForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Bill generated successfully!')
        return redirect('bill_list')
    return render(request, 'hospital/form.html',
                  {'form': form, 'title': 'Generate Bill', 'subtitle': 'Create a new billing record', 'icon': 'file-invoice-dollar', 'back_url': 'bill_list'})


@login_required
def bill_edit(request, pk):
    if request.user.role != 'admin':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    bill = get_object_or_404(Bill, pk=pk)
    form = BillForm(request.POST or None, instance=bill)
    if form.is_valid():
        form.save()
        messages.success(request, 'Bill updated!')
        return redirect('bill_list')
    return render(request, 'hospital/form.html',
                  {'form': form, 'title': f'Edit Bill #{bill.bill_id}', 'subtitle': 'Update billing information', 'icon': 'edit', 'back_url': 'bill_list'})


@login_required
def bill_delete(request, pk):
    if request.user.role != 'admin':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    bill = get_object_or_404(Bill, pk=pk)
    if request.method == 'POST':
        bill.delete()
        messages.success(request, 'Bill removed.')
        return redirect('bill_list')
    return render(request, 'hospital/confirm_delete.html',
                  {'object': bill, 'type': 'Bill', 'back_url': 'bill_list'})


@login_required
def prescription_delete(request, pk):
    if request.user.role not in ['admin', 'doctor']:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    p = get_object_or_404(Prescription, pk=pk)
    appt_pk = p.appointment.pk
    if request.method == 'POST':
        p.delete()
        messages.success(request, 'Prescription removed.')
    return redirect('appointment_detail', pk=appt_pk)
@login_required
def bill_pay(request, pk):
    # Ensure only patients can access this
    if request.user.role != 'patient':
        messages.error(request, 'Access denied. Only patients can make payments.')
        return redirect('dashboard')
        
    try:
        # Fetch the bill, ensuring it belongs to the logged-in patient
        bill = get_object_or_404(Bill, pk=pk, patient=request.user.patient_profile)
    except Exception:
        messages.error(request, 'Patient profile error.')
        return redirect('dashboard')

    # Don't allow paying an already paid bill
    if bill.status == 'Paid':
        messages.info(request, 'This bill has already been paid.')
        return redirect('bill_list')

    if request.method == 'POST':
        # Simulate a successful payment processing
        bill.status = 'Paid'
        bill.paid_amount = bill.amount
        bill.save()
        
        messages.success(request, f'Payment of ₹{bill.amount} was successful! Thank you.')
        return redirect('bill_list')

    return render(request, 'hospital/bill_pay.html', {
        'bill': bill,
        'title': 'Secure Checkout',
        'back_url': 'bill_list'
    })
    
import string
import random
from django.contrib.auth import update_session_auth_hash

def generate_temp_password(length=8):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))