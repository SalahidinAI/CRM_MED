from django.urls import path, include
from .views import *


urlpatterns = [
    # authorization
    path('login/', CustomLoginView.as_view(), name='login'),

    # ✅ patient
    path('department/<int:pk>/patient/', DepartmentPatientAPIView.as_view(), name='department_patients'),
    path('patient/create/', PatientCreateAPIView.as_view(), name='patient_create'),
    path('patient/<int:pk>/edit/', PatientEditAPIView.as_view(), name='patient_edit'),
    path('patient/<str:patient_name>/history/', PatientHistoryAPIView.as_view(), name='patient_history'),
    path('patient/<str:patient_name>/history_of_appointment/', PatientHistoryAppointmentAPIView.as_view(), name='patient_history_of_appointments'),
    path('patient/<str:patient_name>/history_of_payment/', PatientHistoryPaymentAPIView.as_view(), name='patient_history_of_payment'),
    path('patient/<int:pk>/info/', PatientInfoAPIView.as_view(), name='patient_info'),

    # ✅ receptionist
    path('receptionist/<int:pk>/', ReceptionistEditAPIView.as_view(), name='receptionist_edit'),

    # ✅ doctor
    path('doctor/', DoctorListAPIView.as_view(), name='doctor_list'),
    path('doctor/<int:pk>/', DoctorEditAPIView.as_view(), name='doctor_edit'),
    path('doctor/notification/', DoctorNotificationAPIView.as_view(), name='doctor_edit'),
    path('doctor/create/', DoctorCreateAPIView.as_view(), name='doctor_create'),

    # ✅ department
    path('department_service/', DepartmentServiceAPIView.as_view(), name='department_list_services'),

    # ✅ report
    path('report/exact/', ReportExactAPIView.as_view(), name='report_exact'),
    path('report/doctor/', ReportDoctorAPIView.as_view(), name='report_doctor'),
    path('report/summary/', ReportSummaryAPIView.as_view(), name='report_summary'),

    # ✅ analysis
    path('analysis/', AnalysisAPIView.as_view(), name='analysis_regression'),

    # ✅ reset password
    path('password_reset/verify_code/', verify_reset_code, name='verify_reset_code'),
    path('password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
]
