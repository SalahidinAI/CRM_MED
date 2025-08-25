from datetime import timedelta
from django.utils.dateparse import parse_date
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status
from .models import *
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django_rest_passwordreset.models import ResetPasswordToken


User = get_user_model()

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Пользователь с таким email не найден")

        if not (user.check_password(password) or user.password == password):
            raise serializers.ValidationError("Неверный пароль")

        if not user.is_active:
            raise serializers.ValidationError("Пользователь не активен")

        self.context['user'] = user
        return data

    def to_representation(self, instance):
        user = self.context['user']
        refresh = RefreshToken.for_user(user)

        return {
            'user': {
                'username': user.username,
                'email': user.email,
                'role': user.user_role,
            },
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'


class ReceptionistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receptionist
        fields = '__all__'


class ReceptionistNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receptionist
        fields = ['id', 'username']


class JobTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobTitle
        fields = ['job_title']


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'


class DepartmentNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'department_name']


class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = '__all__'


class DoctorCreateEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ['username', 'password', 'profile_image', 'department', 'job_title',
                  'phone', 'room', 'email', 'bonus']


class DoctorNotificationSerializer(serializers.ModelSerializer):
    department = DepartmentNameSerializer()
    registrar = ReceptionistNameSerializer()
    appointment_date = serializers.DateTimeField(format('%d-%m-%Y %H:%M'))

    class Meta:
        model = Patient
        fields = ['id', 'name', 'appointment_date', 'department', 'registrar']


class DoctorListSerializer(serializers.ModelSerializer):
    department = DepartmentNameSerializer()
    job_title = JobTitleSerializer()

    class Meta:
        model = Doctor
        fields = ['id', 'username', 'room', 'department', 'phone', 'job_title']


class DoctorNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ['id', 'username']


class ServiceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceType
        fields = ['id', 'type', 'price']


class ServiceTypeOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceType
        fields = ['id', 'type']


class DoctorPatientSerializer(serializers.ModelSerializer):
    birthday = serializers.DateField(format('%d-%m-%Y'))
    created_date = serializers.DateField(format('%d-%m-%Y'))
    appointment_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M")
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    payment_type_display = serializers.CharField(source='get_payment_type_display', read_only=True)
    patient_status_display = serializers.CharField(source='get_patient_status_display', read_only=True)
    service_type = ServiceTypeOnlySerializer()
    department = DepartmentNameSerializer()
    doctor = DoctorListSerializer()
    # doctor_name = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = ['id', 'name', 'phone', 'birthday', 'appointment_date', 'gender_display',
                  'payment_type_display', 'patient_status_display', 'with_discount', 'created_date',
                  'service_type', 'department', 'doctor']

    # def get_doctor_name(self, obj):
    #     return obj.doctor.job_title


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = '__all__'


class PatientEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['name', 'phone', 'service_type', 'birthday', 'department', 'registrar',
                  'appointment_date', 'gender', 'doctor', 'payment_type', 'patient_status',
                  'with_discount', 'info']


class PatientCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['name', 'phone', 'service_type', 'birthday', 'department', 'registrar',
                  'appointment_date', 'gender', 'doctor', 'payment_type', 'patient_status',
                  'with_discount']


class PatientHistoryAppointmentSerializer(serializers.ModelSerializer):
    registrar = ReceptionistNameSerializer()
    department = DepartmentNameSerializer()
    doctor = DoctorNameSerializer()
    service_type = ServiceTypeOnlySerializer()
    created_date = serializers.DateField(format='%d-%m-%Y')
    appointment_date = serializers.DateTimeField(format='%d-%m-%Y %H:%M')
    patient_status_display = serializers.CharField(source='get_patient_status_display', read_only=True)

    class Meta:
        model = Patient
        fields = ['id', 'name', 'registrar', 'department', 'doctor', 'service_type',
                  'appointment_date', 'created_date', 'patient_status_display']


class PatientHistoryPaymentSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    department = DepartmentNameSerializer()
    doctor = DoctorNameSerializer()
    service_type = ServiceTypeOnlySerializer()
    appointment_date = serializers.DateTimeField(format='%d-%m-%Y %H:%M')
    payment_type_display = serializers.CharField(source='get_payment_type_display', read_only=True)

    class Meta:
        model = Patient
        fields = ['id', 'name', 'department', 'doctor', 'service_type',
                  'appointment_date', 'payment_type_display', 'price']

    def get_price(self, obj):
        if obj.with_discount:
            return obj.with_discount
        return obj.service_type.price


class PatientInfoSerializer(serializers.ModelSerializer):
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)

    class Meta:
        model = Patient
        fields = ['id', 'name', 'phone', 'gender_display', 'info']


class PatientListSerializer(serializers.ModelSerializer):
    payment_type_display = serializers.CharField(source='get_payment_type_display', read_only=True)
    doctor = DoctorNameSerializer()
    price = serializers.SerializerMethodField()
    appointment_date = serializers.DateTimeField(format('%d-%m-%Y %H:%M'))

    class Meta:
        model = Patient
        fields = ['id', 'appointment_date', 'name', 'doctor',
                  'payment_type_display', 'price']

    def get_price(self, obj):
        if obj.with_discount:
            return obj.with_discount
        return obj.service_type.price


class DepartmentPatientSerializer(serializers.ModelSerializer):
    patients = PatientListSerializer(many=True, read_only=True)

    class Meta:
        model = Department
        fields = ['id', 'department_name', 'patients']


class DepartmentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'department_name']


class DepartmentServicesSerializer(serializers.ModelSerializer):
    department_services = ServiceTypeSerializer(many=True, read_only=True)

    class Meta:
        model = Department
        fields = ['id', 'department_name', 'department_services']


class ReportPatientSerializer(serializers.ModelSerializer):
    appointment_date = serializers.DateTimeField(format='%d-%m-%Y %H:%M')
    price = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = ['id', 'name', 'appointment_date', 'price']

    def get_price(self, obj):
        if obj.with_discount:
            return obj.with_discount
        return obj.service_type.price


class ReportDoctorSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    appointment_date = serializers.DateTimeField(format='%d-%m-%Y %H:%M')

    class Meta:
        model = Patient
        fields = ['id', 'name', 'appointment_date', 'price']

    def get_price(self, obj):
        return obj.with_discount if obj.with_discount else obj.service_type.price


class DoctorBonusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ['bonus']


class ReportExactSerializer(serializers.ModelSerializer):
    appointment_date = serializers.DateTimeField(format='%d-%m-%Y %H:%M')
    price = serializers.SerializerMethodField()
    discount_price = serializers.SerializerMethodField()
    service_type = ServiceTypeOnlySerializer()
    payment_type_display = serializers.CharField(source='get_payment_type_display', read_only=True)
    doctor = DoctorBonusSerializer()

    class Meta:
        model = Patient
        fields = ['id', 'appointment_date', 'name', 'service_type',
                  'payment_type_display', 'price', 'discount_price',
                  'doctor']

    def get_price(self, obj):
        return '-' if obj.with_discount else obj.service_type.price

    def get_discount_price(self, obj):
        discount_price = obj.with_discount
        return discount_price if discount_price else '-'


class ReportSummarySerializer(serializers.SerializerMethodField):
    doctor_cash = serializers.IntegerField()
    doctor_card = serializers.IntegerField()
    clinic_cash = serializers.IntegerField()
    clinic_card = serializers.IntegerField()
    total_cash = serializers.IntegerField()
    total_card = serializers.IntegerField()
    total_clinic = serializers.IntegerField()
    total_doctor = serializers.IntegerField()


class VerifyResetCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()  # Email пользователя
    reset_code = serializers.IntegerField()  # 4-значный код
    new_password = serializers.CharField(write_only=True)  # Новый пароль

    def validate(self, data):
        email = data.get('email')
        reset_code = data.get('reset_code')

        # Проверяем, существует ли указанный код для email
        try:
            token = ResetPasswordToken.objects.get(user__email=email, key=reset_code)
        except ResetPasswordToken.DoesNotExist:
            raise serializers.ValidationError("Неверный код сброса или email.")

        data['user'] = token.user
        return data

    def save(self):
        user = self.validated_data['user']
        new_password = self.validated_data['new_password']

        # Устанавливаем новый пароль
        user.set_password(new_password)
        user.save()


class DoctorForCalendar(serializers.ModelSerializer):
    job_title = JobTitleSerializer()

    class Meta:
        model = Doctor
        fields = ['username', 'job_title']


class CalendarReport(serializers.ModelSerializer):
    patient_status_display = serializers.CharField(source='get_patient_status_display', read_only=True)
    appointment_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M")
    appointment_date_end = serializers.SerializerMethodField()
    doctor = DoctorForCalendar(read_only=True)
    department = DepartmentNameSerializer()

    class Meta:
        model = Patient
        fields = ['id', 'patient_status_display', 'department', 'appointment_date',
                  'appointment_date_end', 'doctor']

    def get_appointment_date_end(self, obj):
        date_end = obj.appointment_date + timedelta(minutes=15)
        return date_end.strftime('%d-%m-%Y %H:%M')

