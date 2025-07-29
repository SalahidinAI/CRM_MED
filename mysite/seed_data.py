import os
import random
from datetime import datetime, timedelta
from faker import Faker

import django
from django.utils.crypto import get_random_string

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from crm_med.models import (
    Admin, Receptionist, Doctor, Department, JobTitle, Room,
    ServiceType, Patient
)

fake = Faker()

# ------------------------
# Утилиты генерации данных
# ------------------------

def clear_old_data():
    """Удаляем старые данные."""
    print("Очистка старых данных...")
    Patient.objects.all().delete()
    ServiceType.objects.all().delete()
    Doctor.objects.all().delete()
    Receptionist.objects.all().delete()
    Room.objects.all().delete()
    JobTitle.objects.all().delete()
    Department.objects.all().delete()
    print("Старые данные удалены.")


def create_simple_objects(model, field, count, value_func):
    """Создает объекты с одним текстовым полем."""
    objects = [model(**{field: value_func()}) for _ in range(count)]
    model.objects.bulk_create(objects)
    return list(model.objects.all())


def create_departments(count):
    return create_simple_objects(Department, 'department_name', count, fake.unique.company)


def create_job_titles(count):
    return create_simple_objects(JobTitle, 'job_title', count, fake.unique.job)


def create_rooms(count):
    return create_simple_objects(Room, 'room_number', count, lambda: random.randint(1, 999))


def create_users(model, count, **extra_fields):
    """Генерируем пользователей через create_user."""
    users = []
    for _ in range(count):
        username = fake.unique.user_name()
        users.append(model.objects.create_user(
            username=username,
            email=fake.unique.email(),
            password='password123',
            **extra_fields
        ))
    return users


def create_receptionists(count):
    return create_users(Receptionist, count, role='receptionist')


def create_doctors(count, departments, job_titles, rooms):
    doctors = []
    for _ in range(count):
        doctors.append(Doctor.objects.create_user(
            username=fake.unique.user_name(),
            email=fake.unique.email(),
            password='password123',
            role='doctor',
            department=random.choice(departments),
            job_title=random.choice(job_titles),
            room=random.choice(rooms),
            bonus=random.randint(5, 50)
        ))
    return doctors


def create_services(count, departments):
    services = [
        ServiceType(
            department=random.choice(departments),
            type=fake.unique.word(),
            price=random.randint(500, 5000)
        )
        for _ in range(count)
    ]
    ServiceType.objects.bulk_create(services)
    return list(ServiceType.objects.all())


def create_patients(count, doctors, services, departments, receptionists):
    """Генерация пациентов."""
    patients = []
    for _ in range(count):
        patients.append(Patient(
            name=fake.name(),
            phone=fake.phone_number(),
            service_type=random.choice(services),
            birthday=fake.date_of_birth(minimum_age=1, maximum_age=90),
            department=random.choice(departments),
            registrar=random.choice(receptionists),
            appointment_date=datetime.now() + timedelta(days=random.randint(1, 30)),
            gender=random.choice(['male', 'female']),
            doctor=random.choice(doctors),
            payment_type=random.choice(['cash', 'card']),
            patient_status=random.choice(['pre-registration', 'waiting', 'had an appointment', 'canceled']),
            with_discount=random.choice([None, random.randint(300, 4000)]),
            info=fake.sentence(),
        ))
    Patient.objects.bulk_create(patients)


# ------------------------
# Основная функция
# ------------------------

def run():
    clear_old_data()

    print("Создание новых данных...")

    # Параметры
    department_count = 10
    job_title_count = 10
    room_count = 20
    receptionist_count = 10
    doctor_count = 30
    service_count = 50
    patient_count = 200

    # Генерация
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
