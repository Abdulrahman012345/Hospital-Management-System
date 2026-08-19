from django import forms
from .models import User, Doctor, Patient, Appointment, Prescription, Bill


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-input', 'placeholder': 'Username', 'autocomplete': 'username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-input', 'placeholder': 'Password', 'autocomplete': 'current-password'
    }))


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-input', 'placeholder': 'Create password'
    }))
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={
        'class': 'form-input', 'placeholder': 'Confirm password'
    }))
    
    # --- Patient specific fields ---
    age = forms.IntegerField(min_value=0, max_value=120, required=True, widget=forms.NumberInput(attrs={
        'class': 'form-input', 'placeholder': 'e.g. 25'
    }))
    gender = forms.ChoiceField(choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], widget=forms.Select(attrs={
        'class': 'form-input'
    }))
    blood_group = forms.ChoiceField(choices=[('','Select Blood Group'), ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')], required=False, widget=forms.Select(attrs={
        'class': 'form-input'
    }))
    address = forms.CharField(required=False, widget=forms.Textarea(attrs={
        'class': 'form-input', 'rows': 3, 'placeholder': 'Full residential address'
    }))
    emergency_contact = forms.CharField(label="Emergency Contact", required=False, widget=forms.TextInput(attrs={
        'class': 'form-input', 'placeholder': 'Relative or friend contact'
    }))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'phone']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Last name'}),
            'username': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email address'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Phone number'}),
        }

    def clean(self):
        cd = super().clean()
        if cd.get('password') != cd.get('password2'):
            raise forms.ValidationError('Passwords do not match.')
        return cd
    
class PatientAppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['doctor', 'appointment_date', 'appointment_time', 'reason']
        widgets = {
            'doctor': forms.Select(attrs={'class': 'form-input'}),
            'appointment_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'appointment_time': forms.TimeInput(attrs={'class': 'form-input', 'type': 'time'}),
            'reason': forms.Textarea(attrs={
                'class': 'form-input', 
                'rows': 3, 
                'placeholder': 'Briefly describe your symptoms or reason for visit...'
            }),
        }   
class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['name', 'specialization', 'contact', 'email', 'experience_years', 'available_days']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Full Name'}),
            'specialization': forms.Select(attrs={'class': 'form-input'}),
            'contact': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+91 XXXXX XXXXX'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'doctor@hospital.com'}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-input', 'min': 0}),
            'available_days': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Mon-Fri'}),
        }


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['name', 'age', 'gender', 'contact', 'email', 'address', 'blood_group', 'emergency_contact']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Full Name'}),
            'age': forms.NumberInput(attrs={'class': 'form-input', 'min': 0, 'max': 150}),
            'gender': forms.Select(attrs={'class': 'form-input'}),
            'contact': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+91 XXXXX XXXXX'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'patient@email.com'}),
            'address': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'blood_group': forms.Select(attrs={'class': 'form-input'}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-input'}),
        }


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['patient', 'doctor', 'appointment_date', 'appointment_time', 'status', 'reason', 'notes']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-input'}),
            'doctor': forms.Select(attrs={'class': 'form-input'}),
            'appointment_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'appointment_time': forms.TimeInput(attrs={'class': 'form-input', 'type': 'time'}),
            'status': forms.Select(attrs={'class': 'form-input'}),
            'reason': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'notes': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
        }


class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['medicine', 'dosage', 'duration', 'instructions']
        widgets = {
            'medicine': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Medicine name'}),
            'dosage': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. 500mg twice daily'}),
            'duration': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. 7 days'}),
            'instructions': forms.Textarea(attrs={'class': 'form-input', 'rows': 2, 'placeholder': 'Special instructions...'}),
        }


class BillForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = ['patient', 'appointment', 'amount', 'paid_amount', 'due_date', 'status', 'description']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-input'}),
            'appointment': forms.Select(attrs={'class': 'form-input'}),
            'amount': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'min': '0'}),
            'paid_amount': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'min': '0'}),
            'due_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
        }
