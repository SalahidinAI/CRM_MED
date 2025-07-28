from rest_framework import generics, views, status
from .models import *
from .serializers import *
from rest_framework.response import Response
from django.db.models import Q


class PatientListAPIView(generics.ListAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientListSerializer


class PatientEditAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientEditSerializer


class PatientCreateAPIView(views.APIView):
    def post(self, request):
        serializer = PatientCreateSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            name = data.get("name")
            patient_name_db = Patient.objects.filter(name__iexact=name).exists()
            serializer.save(primary_patient=not patient_name_db)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PatientHistoryAPIView(generics.ListAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientHistoryAppointmentSerializer

    def get_queryset(self):
        patient_name = self.kwargs.get('patient_name')
        return Patient.objects.filter(name=patient_name)


class PatientHistoryAppointmentAPIView(generics.ListAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientHistoryAppointmentSerializer

    def get_queryset(self):
        patient_name = self.kwargs.get('patient_name')
        return Patient.objects.filter(
            Q(name=patient_name) &
            Q(patient_status='had an appointment')
        )


class PatientHistoryPaymentAPIView(generics.ListAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientHistoryPaymentSerializer

    def get_queryset(self):
        patient_name = self.kwargs.get('patient_name')
        return Patient.objects.filter(
            Q(name=patient_name) &
            Q(patient_status='had an appointment')
        )


class PatientInfoAPIView(generics.RetrieveAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientInfoSerializer


class DoctorListAPIView(generics.ListAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorListSerializer


class UserProfileAPIView(generics.ListAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


class AdminAPIView(generics.ListAPIView):
    queryset = Admin.objects.all()
    serializer_class = AdminSerializer


class ReceptionistAPIView(generics.ListAPIView):
    queryset = Receptionist.objects.all()
    serializer_class = ReceptionistSerializer


class DepartmentAPIView(generics.ListAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentNameSerializer


class JobTitleAPIView(generics.ListAPIView):
    queryset = JobTitle.objects.all()
    serializer_class = JobTitleSerializer


class RoomAPIView(generics.ListAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer


class ServiceTypeAPIView(generics.ListAPIView):
    queryset = ServiceType.objects.all()
    serializer_class = ServiceTypeSerializer
