from django.db import migrations, models
import django.db.models.deletion
import django.contrib.auth.models
import django.contrib.auth.validators
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False)),
                ('username', models.CharField(max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()])),
                ('first_name', models.CharField(blank=True, max_length=150)),
                ('last_name', models.CharField(blank=True, max_length=150)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now)),
                ('role', models.CharField(choices=[('admin', 'Admin'), ('doctor', 'Doctor'), ('patient', 'Patient')], default='patient', max_length=10)),
                ('phone', models.CharField(blank=True, max_length=15, null=True)),
                ('groups', models.ManyToManyField(blank=True, related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={'verbose_name': 'user', 'verbose_name_plural': 'users', 'abstract': False},
            managers=[('objects', django.contrib.auth.models.UserManager())],
        ),
        migrations.CreateModel(
            name='Doctor',
            fields=[
                ('doctor_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('specialization', models.CharField(choices=[('Cardiology', 'Cardiology'), ('Neurology', 'Neurology'), ('Orthopedics', 'Orthopedics'), ('Pediatrics', 'Pediatrics'), ('Dermatology', 'Dermatology'), ('General Medicine', 'General Medicine'), ('Gynecology', 'Gynecology'), ('Ophthalmology', 'Ophthalmology'), ('Psychiatry', 'Psychiatry'), ('Radiology', 'Radiology'), ('Surgery', 'Surgery'), ('Urology', 'Urology'), ('ENT', 'ENT'), ('Oncology', 'Oncology'), ('Endocrinology', 'Endocrinology')], max_length=100)),
                ('contact', models.CharField(max_length=15)),
                ('email', models.EmailField(blank=True, null=True)),
                ('experience_years', models.PositiveIntegerField(default=0)),
                ('available_days', models.CharField(default='Mon-Fri', max_length=200)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='doctor_profile', to='hospital.user')),
            ],
        ),
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('patient_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('age', models.IntegerField()),
                ('gender', models.CharField(choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], max_length=10)),
                ('contact', models.CharField(max_length=15)),
                ('email', models.EmailField(blank=True, null=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('blood_group', models.CharField(blank=True, choices=[('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')], max_length=5, null=True)),
                ('emergency_contact', models.CharField(blank=True, max_length=15, null=True)),
                ('registered_on', models.DateField(auto_now_add=True)),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='patient_profile', to='hospital.user')),
            ],
        ),
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('appointment_id', models.AutoField(primary_key=True, serialize=False)),
                ('appointment_date', models.DateField()),
                ('appointment_time', models.TimeField(default='09:00')),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Scheduled', 'Scheduled'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled'), ('No-Show', 'No-Show')], default='Pending', max_length=50)),
                ('reason', models.TextField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hospital.doctor')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hospital.patient')),
            ],
            options={'ordering': ['-appointment_date', '-appointment_time']},
        ),
        migrations.CreateModel(
            name='Prescription',
            fields=[
                ('prescription_id', models.AutoField(primary_key=True, serialize=False)),
                ('medicine', models.CharField(max_length=200)),
                ('dosage', models.CharField(max_length=100)),
                ('duration', models.CharField(default='7 days', max_length=100)),
                ('instructions', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('appointment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prescriptions', to='hospital.appointment')),
            ],
        ),
        migrations.CreateModel(
            name='Bill',
            fields=[
                ('bill_id', models.AutoField(primary_key=True, serialize=False)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('paid_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('bill_date', models.DateField(auto_now_add=True)),
                ('due_date', models.DateField(blank=True, null=True)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Paid', 'Paid'), ('Partially Paid', 'Partially Paid'), ('Waived', 'Waived')], default='Pending', max_length=20)),
                ('description', models.TextField(blank=True, null=True)),
                ('appointment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='hospital.appointment')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hospital.patient')),
            ],
        ),
    ]
