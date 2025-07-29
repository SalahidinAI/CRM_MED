from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator


ROLE_CHOICES = (
    ('admin', _('Admin')),
    ('receptionist', _('Receptionist')),
    ('doctor', _('Doctor')),
)

GENDER_CHOICES = (
    ('male', _('Male')),
    ('female', _('Female')),
)

PAYMENT_TYPE_CHOICES = (
    ('cash', _('Cash')),
    ('card', _('Card')),
)

PATIENT_STATUS_CHOICES = (
    ('pre-registration', _('Pre-registration')),
    ('waiting', _('Waiting')),
    ('had an appointment', _('Had an appointment')),
    ('canceled', _('Canceled')),
)


class UserProfile(AbstractUser):
    profile_image = models.ImageField(upload_to='user_images/')
    email = models.EmailField(unique=True)
    phone = PhoneNumberField(null=True, blank=True, unique=True)

    def __str__(self):
        return f'{self.username}'

    class Meta:
        verbose_name = 'Main UserProfile'


class Admin(UserProfile):
    role = models.CharField(max_length=16, choices=ROLE_CHOICES, default='admin')

    def __str__(self):
        return f'{self.username}'

    class Meta:
        verbose_name = 'Admin'


class Receptionist(UserProfile):
    role = models.CharField(max_length=16, choices=ROLE_CHOICES, default='receptionist')

    def __str__(self):
        return f'{self.username}'

    class Meta:
        verbose_name = 'Receptionist'


class Department(models.Model):
    department_name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return f'{self.department_name}'


class JobTitle(models.Model):
    job_title = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return f'{self.job_title}'


class Room(models.Model):
    room_number = models.PositiveSmallIntegerField(unique=True)

    def __str__(self):
        return f'{self.room_number}'


class Doctor(UserProfile):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    job_title = models.ForeignKey(JobTitle, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True, blank=True)
    bonus = models.PositiveSmallIntegerField(default=5, validators=[
        MinValueValidator(5), MaxValueValidator(60)
    ])
    role = models.CharField(max_length=16, choices=ROLE_CHOICES, default='doctor')

    def __str__(self):
        return f'{self.username} - {self.room}'

    class Meta:
        verbose_name = 'Doctor'

    def get_analysis(self):
        patients = self.doctor_patients.select_related('service_type').all()
        if not patients:
            return {
                'rise': 50,
                'fall': 50,
                'patient_count': 0,
                'patient_primary_count': 0,
            }

        previous = patients[0].with_discount or patients[0].service_type.price
        up = 0
        down = 0
        patient_count = 1
        patient_primary_count = 0

        for patient in patients[1:]:
            patient_count += 1
            if patient.primary_patient:
                patient_primary_count += 1

            price = patient.with_discount or patient.service_type.price
            if previous < price:
                up += price - previous
            else: down += previous - price
            previous = price

        top = up * 2
        fall = down / top * 100
        rise = 100 - fall
        return {
            'rise': rise,
            'fall': fall,
            'patient_count': patient_count,
            'patient_primary_count': patient_primary_count,
        }

    @classmethod
    def get_analysis_data(cls):
        doctors = cls.objects.all()
        if not doctors.exists():
            return {'rise': 0, 'fall': 0}

        rise_list = []
        fall_list = []

        doctor_count = 0
        patient_count_total = 0
        patient_primary_count_total = 0
        for doctor in doctors:
            doctor_count += 1
            analysis = doctor.get_analysis()
            rise_list.append(analysis['rise'])
            fall_list.append(analysis['fall'])
            patient_count_total += analysis['patient_count']
            patient_primary_count_total += analysis['patient_primary_count']

        doctor_count = len(rise_list)
        rise = sum(rise_list) / doctor_count
        fall = sum(fall_list) / doctor_count
        patient_primary_percent = round(patient_primary_count_total / patient_count_total * 100)
        patient_repeatedly_percent = 100 - patient_primary_percent

        return {
            'rise': round(rise),
            'fall': -round(fall),
            'doctor_count': doctor_count,
            'patient_count_total': patient_count_total,
            'patient_primary_percent': patient_primary_percent,
            'patient_repeatedly_percent': patient_repeatedly_percent,
        }

    def get_cash_and_card_payment(self):
        patients = self.doctor_patients.select_related('service_type').all()
        cash = 0
        card = 0
        for i in patients:
            discount = i.with_discount
            service_price = i.service_type.price

            if i.payment_type == 'cash':
                cash += discount if discount else service_price
            else:
                card += discount if discount else service_price
        return {
            'cash': cash,
            'card': card,
        }

    @classmethod
    def get_all_payment(cls):
        doctor_cash = 0
        doctor_card = 0

        clinic_cash = 0
        clinic_card = 0

        total_cash = 0
        total_card = 0

        total_clinic = 0
        total_doctor = 0
        for doctor in cls.objects.all():
            cash = doctor.get_cash_and_card_payment()['cash']
            card = doctor.get_cash_and_card_payment()['card']

            # оплачено докторам: нал / без нал
            doctor_cash += cash / 100 % doctor.bonus if doctor.bonus else 1
            doctor_card += card / 100 % doctor.bonus if doctor.bonus else 1

            # оплачено клинике: нал / без нал
            clinic_cash += cash - doctor_cash
            clinic_card += card - doctor_card

            # оплачено в целом: нал / без нал
            total_cash += cash
            total_card += card

            # оплачено клинике в целом: нал + без нал
            total_clinic += clinic_cash + clinic_card

            # оплачено докторам в целом: нал + без нал
            total_doctor += doctor_cash + doctor_card

        return {
            'doctor_cash': int(doctor_cash),
            'doctor_card': int(doctor_card),

            'clinic_cash': int(clinic_cash),
            'clinic_card': int(clinic_card),

            'total_cash': int(total_cash),
            'total_card': int(total_card),

            'total_clinic': int(total_clinic),
            'total_doctor': int(total_doctor),
        }


class ServiceType(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='department_services')
    type = models.CharField(max_length=32)
    price = models.PositiveSmallIntegerField()

    def __str__(self):
        return f'{self.department}: {self.type} - {self.price}'

    class Meta:
        unique_together = ('type', 'department')


class Patient(models.Model):
    name = models.CharField(max_length=64)
    phone = PhoneNumberField()
    service_type = models.ForeignKey(ServiceType, on_delete=models.CASCADE)
    birthday = models.DateField()
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='patients')
    registrar = models.ForeignKey(Receptionist, on_delete=models.CASCADE)
    appointment_date = models.DateTimeField()
    gender = models.CharField(max_length=16, choices=GENDER_CHOICES)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='doctor_patients')
    payment_type = models.CharField(max_length=32, choices=PAYMENT_TYPE_CHOICES)
    patient_status = models.CharField(max_length=32, choices=PATIENT_STATUS_CHOICES)
    with_discount = models.PositiveSmallIntegerField(null=True, blank=True)
    created_date = models.DateField(auto_now_add=True)
    primary_patient = models.BooleanField(null=True, blank=True)
    info = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'{self.name}'



# ADMIN:
# image
# username
# email
# phone
# password
# role


# RECEPTIONIST:
# image
# username
# email
# phone
# password
# role (foreignkey) (admin, receptionist, dentist, surgeon)


# DOCTOR:
# image
# username (first and last)
# phone
# department (foreignkey)
# role
# job_title (foreignkey) (receptionist, dentist, surgeon)
# password
# room (foreignkey)
# email
# bonus %

# PATIENT:
# name (first and last)
# phone
# service_type (choices) (type and price должны быть отдельными полями + foreignkey -> department)
# birthday (date)
# department (foreignkey)
# registrar (регистратор) foreignkey
# date_appointment (datetime)
# gender (choices)
# doctor (Foreignkey)
# payment_type (наличные или перевод) choices)
# patient_status (choices) (предварительная запись, в ожидании, был в приеме, отменено)
# with_discount (сумма оплаты) (если это поле пуста то будем считать сумму в service_type
# created_date (date)
