from datetime import timedelta

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


class ReportExactAPIView(generics.RetrieveAPIView):
    queryset = Doctor.objects.all()
    serializer_class = ReportExactSerializer


# class AnalysisAPIView(APIView):
#     def get(self, request):
#         period = request.query_params.get("period", "weekly")
#
#         now = timezone.now().date()
#         trunc_map = {
#             'daily': TruncDay,
#             'weekly': TruncWeek,
#             'monthly': TruncMonth,
#             'yearly': TruncYear
#         }
#         delta_map = {
#             'daily': 1,
#             'weekly': 7,
#             'monthly': 30,
#             'yearly': 365
#         }
#
#         if period not in trunc_map:
#             return Response({"error": "Invalid period"}, status=400)
#
#         trunc_func = trunc_map[period]
#         start_date = now - timedelta(days=delta_map[period])
#
#         # Основной график
#         chart_data = (
#             Patient.objects
#             .filter(appointment_date__gte=start_date)
#             .annotate(period=trunc_func("appointment_date"))
#             .values("period")
#             .annotate(
#                 total=Count("id"),
#                 canceled=Count("id", filter=Q(patient_status='canceled'))
#             )
#             .order_by("period")
#         )
#         analysis = Doctor.get_analysis_data()
#         return Response({
#             'analysis': analysis,
#             'chart': chart_data,
#         })


class AnalysisAPIView(APIView):
    def get(self, request):
        period = request.query_params.get("period", "weekly")

        now = timezone.now().date()
        trunc_map = {
            'daily': TruncDay,
            'weekly': TruncWeek,
            'monthly': TruncMonth,
            'yearly': TruncYear
        }
        delta_map = {
            'daily': 1,
            'weekly': 7,
            'monthly': 30,
            'yearly': 365
        }

        if period not in trunc_map:
            return Response({"error": "Invalid period"}, status=400)

        trunc_func = trunc_map[period]
        start_date = now - timedelta(days=delta_map[period])

        # Основной график
        chart_data = (
            Patient.objects
            .filter(appointment_date__gte=start_date)
            .annotate(period=trunc_func("appointment_date"))
            .values("period")
            .annotate(
                total=Count("id"),
                canceled=Count("id", filter=Q(patient_status='canceled'))
            )
            .order_by("period")
        )
        analysis = Doctor.get_analysis_data()
        return Response({
            'analysis': analysis,
            'chart': chart_data,
        })


class ReportSummaryAPIView(APIView):
    def get(self, request):
        total = Doctor.get_all_payment()
        return Response({"general_payment": total})


class AnalysisRegressionAPIView(APIView):
    def get(self, request):
        period = request.query_params.get("period", "weekly")

        now = timezone.now().date()
        trunc_map = {
            'daily': TruncDay,
            'weekly': TruncWeek,
            'monthly': TruncMonth,
            'yearly': TruncYear
        }
        delta_map = {
            'daily': 1,
            'weekly': 7,
            'monthly': 30,
            'yearly': 365
        }

        if period not in trunc_map:
            return Response({"error": "Invalid period"}, status=400)

        trunc_func = trunc_map[period]
        start_date = now - timedelta(days=delta_map[period])

        # Основной график
        chart_data = (
            Patient.objects
            .filter(appointment_date__gte=start_date)
            .annotate(period=trunc_func("appointment_date"))
            .values("period")
            .annotate(
                total=Count("id"),
                canceled=Count("id", filter=Q(patient_status='canceled'))
            )
            .order_by("period")
        )

        # Общие метрики
        total_doctors = Doctor.objects.count()

        total_patients = Patient.objects.filter(appointment_date__gte=start_date).count()
        unique_patients_set = set()
        repeated = 0
        new = 0

        for p in Patient.objects.filter(appointment_date__gte=start_date).order_by('appointment_date'):
            key = (p.name.strip().lower(), str(p.phone))
            if key in unique_patients_set:
                repeated += 1
            else:
                unique_patients_set.add(key)
                new += 1

        new_percent = round((new / max(total_patients, 1)) * 100)
        repeated_percent = 100 - new_percent

        # Рост и падение (сравниваем с предыдущим периодом)
        prev_start = start_date - timedelta(days=delta_map[period])
        prev_count = Patient.objects.filter(appointment_date__gte=prev_start, appointment_date__lt=start_date).count()
        current_count = total_patients

        growth = current_count - prev_count
        trend = "up" if growth > 0 else ("down" if growth < 0 else "same")

        return Response({
            "total_doctors": total_doctors,
            "total_clients": len(unique_patients_set),
            "new_percent": new_percent,
            "repeated_percent": repeated_percent,
            "growth": growth,
            "trend": trend,
            "chart": chart_data,
        })


# class AnalysisRegressionAPIView(APIView):
#     def get(self, request):
#         period = request.query_params.get("period", "weekly")
#
#         now = timezone.now().date()
#         trunc_map = {
#             'daily': TruncDay,
#             'weekly': TruncWeek,
#             'monthly': TruncMonth,
#             'yearly': TruncYear
#         }
#         delta_map = {
#             'daily': 1,
#             'weekly': 7,
#             'monthly': 30,
#             'yearly': 365
#         }
#
#         if period not in trunc_map:
#             return Response({"error": "Invalid period"}, status=400)
#
#         trunc_func = trunc_map[period]
#         start_date = now - timedelta(days=delta_map[period])
#
#         # Основной график
#         chart_data = (
#             Patient.objects
#             .filter(appointment_date__gte=start_date)
#             .annotate(period=trunc_func("appointment_date"))
#             .values("period")
#             .annotate(
#                 total=Count("id"),
#                 canceled=Count("id", filter=Q(patient_status='canceled'))
#             )
#             .order_by("period")
#         )
#
#         # Общие метрики
#         total_doctors = Doctor.objects.count()
#
#         total_patients = Patient.objects.filter(appointment_date__gte=start_date).count()
#         unique_patients_set = set()
#         repeated = 0
#         new = 0
#
#         for p in Patient.objects.filter(appointment_date__gte=start_date).order_by('appointment_date'):
#             key = (p.name.strip().lower(), str(p.phone))
#             if key in unique_patients_set:
#                 repeated += 1
#             else:
#                 unique_patients_set.add(key)
#                 new += 1
#
#         new_percent = round((new / max(total_patients, 1)) * 100)
#         repeated_percent = 100 - new_percent
#
#         # Рост и падение (сравниваем с предыдущим периодом)
#         prev_start = start_date - timedelta(days=delta_map[period])
#         prev_count = Patient.objects.filter(appointment_date__gte=prev_start, appointment_date__lt=start_date).count()
#         current_count = total_patients
#
#         growth = current_count - prev_count
#         trend = "up" if growth > 0 else ("down" if growth < 0 else "same")
#
#         return Response({
#             "total_doctors": total_doctors,
#             "total_clients": len(unique_patients_set),
#             "new_percent": new_percent,
#             "repeated_percent": repeated_percent,
#             "growth": growth,
#             "trend": trend,
#             "chart": chart_data,
#         })