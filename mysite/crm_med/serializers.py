from rest_framework import serializers
from .models import *


# class UserProfileSerializer(serializers.ModelSerializer):
#     role_display = serializers.CharField(source='get_role_display', read_only=True)
#     class Meta:
#         model = UserProfile
#         fields = ['id', 'role', 'role_display']


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'


class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = ['username', 'password', 'profile_image', 'email', 'phone']


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
        fields = '__all__'


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'


class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = '__all__'


class DoctorCreateEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ['username', 'password', 'profile_image', 'department', 'job_title',
                  'phone', 'room', 'email', 'bonus']


class DoctorListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ['id', 'username', 'room', 'department', 'phone']


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


class DepartmentNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'department_name']


class PatientHistoryAppointmentSerializer(serializers.ModelSerializer):
    registrar = ReceptionistNameSerializer()
    department = DepartmentNameSerializer()
    doctor = DoctorNameSerializer()
    service_type = ServiceTypeOnlySerializer()
    created_date = serializers.DateField(format='%d-%m-%Y')
    patient_status_display = serializers.CharField(source='get_patient_status_display', read_only=True)

    class Meta:
        model = Patient
        fields = ['id', 'name', 'registrar', 'department', 'doctor', 'service_type',
                  'created_date', 'patient_status_display']


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
        fields = ['id', 'name', 'phone', 'gender_display']


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


class ReportExactPatientSerializer(serializers.ModelSerializer):
    appointment_date = serializers.DateTimeField(format='%d-%m-%Y %H:%M')
    price = serializers.SerializerMethodField()
    service_type = ServiceTypeOnlySerializer()
    payment_type_display = serializers.CharField(source='get_payment_type_display', read_only=True)

    class Meta:
        model = Patient
        fields = ['id', 'appointment_date', 'name', 'service_type', 'payment_type_display',
                  'price']

    def get_price(self, obj):
        if obj.with_discount:
            return obj.with_discount
        return obj.service_type.price


class ReportDoctorSerializer(serializers.ModelSerializer):
    doctor_patients = ReportPatientSerializer(many=True, read_only=True)

    class Meta:
        model = Doctor
        fields = ['id', 'username', 'doctor_patients']


class ReportExactSerializer(serializers.ModelSerializer):
    doctor_patients = ReportExactPatientSerializer(many=True, read_only=True)

    class Meta:
        model = Doctor
        fields = ['id', 'username', 'bonus', 'doctor_patients']

