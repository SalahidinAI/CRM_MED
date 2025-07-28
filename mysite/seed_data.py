import random
from faker import Faker
from datetime import datetime, timedelta
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')  # <-- путь до settings.py
django.setup()

from crm_med.models import (
    Admin, Receptionist, Doctor, Department, JobTitle, Room,
    ServiceType, Patient
)

fake = Faker()


def create_departments(count):
    return [Department.objects.create(department_name=fake.unique.company()) for _ in range(count)]


def create_job_titles(count):
    return [JobTitle.objects.create(job_title=fake.unique.job()) for _ in range(count)]


def create_rooms(count):
    return [Room.objects.create(room_number=i + 1) for i in range(count)]


def create_receptionists(count):
    return [Receptionist.objects.create_user(
        username=fake.unique.user_name(),
        email=fake.unique.email(),
        password='password123',
        role='receptionist'
    ) for _ in range(count)]


def create_doctors(count, departments, job_titles, rooms):
    return [Doctor.objects.create_user(
        username=fake.unique.user_name(),
        email=fake.unique.email(),
        password='password123',
        role='doctor',
        department=random.choice(departments),
        job_title=random.choice(job_titles),
        room=random.choice(rooms),
        bonus=random.randint(0, 20)
    ) for _ in range(count)]


def create_services(count, departments):
    return [ServiceType.objects.create(
        department=random.choice(departments),
        type=fake.unique.word(),
        price=random.randint(500, 5000)
    ) for _ in range(count)]


def create_patients(count, doctors, services, departments, receptionists):
    patients = []
    for _ in range(count):
        doctor = random.choice(doctors)
        service = random.choice(services)
        patient = Patient.objects.create(
            name=fake.name(),
            phone=fake.phone_number(),
            service_type=service,
            birthday=fake.date_of_birth(minimum_age=1, maximum_age=90),
            department=random.choice(departments),
            registrar=random.choice(receptionists),
            appointment_date=datetime.now() + timedelta(days=random.randint(1, 30)),
            gender=random.choice(['male', 'female']),
            doctor=doctor,
            payment_type=random.choice(['cash', 'card']),
            patient_status=random.choice(['pre-registration', 'waiting', 'had an appointment', 'canceled']),
            with_discount=random.choice([None, random.randint(300, 4000)]),
            info=fake.sentence()
        )
        patients.append(patient)
    return patients


def run():
    print("Очистка старых данных...")
    Patient.objects.all().delete()
    ServiceType.objects.all().delete()
    Doctor.objects.all().delete()
    Receptionist.objects.all().delete()
    Room.objects.all().delete()
    JobTitle.objects.all().delete()
    Department.objects.all().delete()

    print("Создание новых данных...")

    department_count = 10
    job_title_count = 10
    room_count = 20
    receptionist_count = 10
    doctor_count = 30
    service_count = 50
    patient_count = 200

    departments = create_departments(department_count)
    job_titles = create_job_titles(job_title_count)
    rooms = create_rooms(room_count)
    receptionists = create_receptionists(receptionist_count)
    doctors = create_doctors(doctor_count, departments, job_titles, rooms)
    services = create_services(service_count, departments)
    create_patients(patient_count, doctors, services, departments, receptionists)

    print("✅ Генерация завершена!")


if __name__ == '__main__':
    run()
