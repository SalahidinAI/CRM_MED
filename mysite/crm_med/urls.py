from django.urls import path
from .views import *


urlpatterns = [
    path('patient/', PatientListAPIView.as_view(), name='patient_list'),
    path('patient/create/', PatientCreateAPIView.as_view(), name='patient_create'),
    path('patient/<int:pk>/edit/', PatientEditAPIView.as_view(), name='patient_edit'),
    path('patient/<str:patient_name>/history/', PatientHistoryAPIView.as_view(), name='patient_history'),
    path('patient/<str:patient_name>/history_of_appointment/', PatientHistoryAppointmentAPIView.as_view(), name='patient_history_of_appointments'),
    path('patient/<str:patient_name>/history_of_payment/', PatientHistoryPaymentAPIView.as_view(), name='patient_history_of_payment'),
    path('patient/<int:pk>/info', PatientInfoAPIView.as_view(), name='patient_info'),

    # analysis

    path('doctor/', DoctorListAPIView.as_view(), name='doctor_list'),

    path('user/', UserProfileAPIView.as_view(), name='user_list'),
]