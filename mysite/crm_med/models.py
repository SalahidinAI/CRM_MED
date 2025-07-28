from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext_lazy as _


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
    # role = models.CharField(max_length=32, choices=ROLE_CHOICES)

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
    bonus = models.PositiveSmallIntegerField()
    role = models.CharField(max_length=16, choices=ROLE_CHOICES, default='doctor')

    def __str__(self):
        return f'{self.username} - {self.room}'

    class Meta:
        verbose_name = 'Doctor'


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
    # with_discount (сумма оплаты) (если это поле пуста то будем считать сумму в service_type
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
