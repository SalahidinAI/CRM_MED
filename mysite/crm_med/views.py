from datetime import timedelta
from django.utils.dateparse import parse_date
from rest_framework import generics, views, status
from .models import *
from .serializers import *
from rest_framework.response import Response
from django.db.models import Q, Count
from rest_framework.views import APIView
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth, TruncYear
from django.utils import timezone


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


class DoctorEditAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorCreateEditSerializer


class DoctorCreateAPIView(generics.CreateAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorCreateEditSerializer


class UserProfileAPIView(generics.ListAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


class AdminCreateAPIView(generics.CreateAPIView):
    queryset = Admin.objects.all()
    serializer_class = AdminSerializer


class ReceptionistAPIView(generics.ListAPIView):
    queryset = Receptionist.objects.all()
    serializer_class = ReceptionistSerializer


class DepartmentServiceAPIView(generics.ListAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentServicesSerializer


class DepartmentPatientAPIView(generics.RetrieveAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentPatientSerializer


class JobTitleAPIView(generics.ListAPIView):
    queryset = JobTitle.objects.all()
    serializer_class = JobTitleSerializer


class ReportDoctorAPIView(generics.RetrieveAPIView):
    queryset = Doctor.objects.all()
    serializer_class = ReportDoctorSerializer


# class ReportExactAPIView(generics.RetrieveAPIView):
#     queryset = Doctor.objects.all()
#     serializer_class = ReportExactSerializer
#
#     def get_serializer_context(self):
#         context = super().get_serializer_context()
#         date_str = self.request.query_params.get("date")
#
#         if date_str:
#             selected_date = parse_date(date_str)
#             # Фильтруем пациентов для выбранного доктора
#             doctor = self.get_object()
#             patients_qs = doctor.doctor_patients.filter(appointment_date__date=selected_date)
#             context['patients_qs'] = patients_qs
#         return context


class ReportExactAPIView(generics.ListAPIView):
    serializer_class = ReportExactSerializer

    def get_queryset(self):
        # Базовый queryset — все доктора
        queryset = Doctor.objects.all()

        # Фильтр по конкретному врачу (если передан)
        doctor_id = self.request.query_params.get("doctor")
        if doctor_id:
            queryset = queryset.filter(id=doctor_id)

        # Фильтр по отделению
        department_id = self.request.query_params.get("department")
        if department_id:
            queryset = queryset.filter(department_id=department_id)

        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        date_str = self.request.query_params.get("date")
        if date_str:
            selected_date = parse_date(date_str)
            context["selected_date"] = selected_date
        return context


class ReportSummaryAPIView(APIView):
    permission_classes = [] # IsAdministrator, IsReceptionist

    def get(self, request):
        total = Doctor.get_all_payment()
        return Response({"general_payment": total})


class AnalysisAPIView(APIView):
    permission_classes = [] # IsAdministrator

    def get(self, request):
        period = request.query_params.get("period", "weekly")

        now = timezone.now()
        # Настраиваем интервалы
        if period == "daily":
            interval = timedelta(hours=2)  # 12 интервалов
            start_date = now - timedelta(days=1)
        elif period == "weekly":
            interval = timedelta(days=1)  # 7 интервалов
            start_date = now - timedelta(days=7)
        elif period == "monthly":
            interval = timedelta(days=2)  # 15 интервалов
            start_date = now - timedelta(days=30)
        elif period == "yearly":
            interval = None  # Для года будем делить на месяцы
            start_date = now - timedelta(days=365)
        else:
            return Response({"error": "Invalid period"}, status=400)

        patients_qs = Patient.objects.filter(appointment_date__gte=start_date, appointment_date__lte=now)

        # кол-во докторов и пациентов.
        total_doctors = Doctor.objects.count()
        total_patients = patients_qs.count()

        # новые и повторные пациенты.
        primary = 0
        for p in patients_qs:
            if p.primary_patient:
                primary += 1

        primary_percent = 0 if not total_patients else primary / total_patients * 100
        repeated_percent = 0 if not total_patients else 100 - primary_percent

        # рост и падение.
        fall = patients_qs.filter(
            patient_status='canceled',
        ).count()
        fall_percent = 0 if not total_patients else fall / total_patients * 100
        rise_percent = 0 if not total_patients else 100 - fall_percent
        print(f'total: {total_patients}, fall: {fall}, f_per: {fall_percent}, r_per: {rise_percent}')

        # Строим интервалы для chart
        chart = []
        if period == "yearly":
            # 12 интервалов по месяцам
            for m in range(1, 13):
                start_month = start_date.replace(month=m, day=1)
                if m == 12:
                    end_month = start_month.replace(year=start_month.year + 1, month=1, day=1)
                else:
                    end_month = start_month.replace(month=m + 1, day=1)
                bucket_qs = patients_qs.filter(
                    appointment_date__gte=start_month,
                    appointment_date__lt=end_month
                )
                had_an_appointment = bucket_qs.exclude(patient_status='canceled').count()
                canceled = bucket_qs.filter(patient_status='canceled').count()
                chart.append({
                    "appointment_date": start_month,
                    "had_an_appointment": had_an_appointment,
                    "canceled": canceled,
                })
        else:
            current_start = start_date
            while current_start < now:
                current_end = current_start + interval
                bucket_qs = patients_qs.filter(
                    appointment_date__gte=current_start,
                    appointment_date__lt=current_end
                )
                had_an_appointment = bucket_qs.exclude(patient_status='canceled').count()
                canceled = bucket_qs.filter(patient_status='canceled').count()
                chart.append({
                    "appointment_date": current_start,
                    "had_an_appointment": had_an_appointment,
                    "canceled": canceled,
                })
                current_start = current_end

        for row in chart:
            row["appointment_date"] = row["appointment_date"].strftime("%d-%m-%Y %H:%M")

        return Response({
            "total_doctors": total_doctors,
            "total_patients": total_patients,
            "new_percent": round(primary_percent),
            "repeated_percent": round(repeated_percent),
            "rise": round(rise_percent),
            "fall": round(fall_percent),
            "chart": chart,
        })


