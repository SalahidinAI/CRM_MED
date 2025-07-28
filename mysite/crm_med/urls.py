from django.urls import path
from .views import *


urlpatterns = [
    # admin
    path('admin_create/', AdminCreateAPIView.as_view(), name='admin_create'),

    # patient
    path('patient/', PatientListAPIView.as_view(), name='patient_list'),
    path('patient/create/', PatientCreateAPIView.as_view(), name='patient_create'),
    path('patient/<int:pk>/edit/', PatientEditAPIView.as_view(), name='patient_edit'),
    path('patient/<str:patient_name>/history/', PatientHistoryAPIView.as_view(), name='patient_history'),
    path('patient/<str:patient_name>/history_of_appointment/', PatientHistoryAppointmentAPIView.as_view(), name='patient_history_of_appointments'),
    path('patient/<str:patient_name>/history_of_payment/', PatientHistoryPaymentAPIView.as_view(), name='patient_history_of_payment'),
    path('patient/<int:pk>/info', PatientInfoAPIView.as_view(), name='patient_info'),
    path('department/<int:pk>/patient/', DepartmentPatientAPIView.as_view(), name='department_detail'),

    # doctor
    path('doctor/', DoctorListAPIView.as_view(), name='doctor_list'),
    path('doctor/<int:pk>/', DoctorEditAPIView.as_view(), name='doctor_edit'),
    path('doctor/create/', DoctorCreateAPIView.as_view(), name='doctor_create'),

    # department
    path('department/', DepartmentServiceAPIView.as_view(), name='department_list_services'),

    # report
    path('report/doctor/<int:pk>/', ReportDoctorAPIView.as_view(), name='report_doctor')

    # analysis


]
