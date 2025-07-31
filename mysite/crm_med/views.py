from datetime import timedelta
from django.utils.dateparse import parse_date
from rest_framework import generics, views, status
from .serializers import *
from .models import *
from rest_framework.response import Response
from django.db.models import Q
from rest_framework.views import APIView
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from django.db.models import F, Sum, Value, IntegerField, Case, When, Q
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from openpyxl import Workbook
from rest_framework.permissions import IsAuthenticated
from django.utils.translation import gettext as _
import openpyxl
from openpyxl.utils import get_column_letter


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


class ReportDoctorAPIView(generics.ListAPIView):
    """
        Возвращает список пациентов для конкретного доктора и даты.
        Фильтры:
        - doctor (id доктора)
        - date (YYYY-MM-DD)
        """
    serializer_class = ReportDoctorSerializer

    def get_queryset(self):
        qs = Patient.objects.all()

        doctor_id = self.request.query_params.get('doctor')
        date_str = self.request.query_params.get('date')

        if doctor_id:
            qs = qs.filter(doctor_id=doctor_id)

        if date_str:
            selected_date = parse_date(date_str)
            if not selected_date:
                raise ValidationError({"date": "Invalid date format, use YYYY-MM-DD"})
            qs = qs.filter(appointment_date__date=selected_date)

        return qs

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # Проверяем, нужно ли экспортировать Excel
        if request.query_params.get("export") == "excel":
            return self.export_to_excel(queryset)

        serializer = self.get_serializer(queryset, many=True)

        # Считаем сумму цен
        total_price = sum(
            p.with_discount if p.with_discount else p.service_type.price
            for p in queryset
        )

        return Response({
            "total_price": total_price,
            "results": serializer.data
        })

    def export_to_excel(self, queryset):
        # Создаем книгу и лист
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Patients"

        # Заголовки (локализация)
        lang = self.request.LANGUAGE_CODE
        if lang == 'ru':
            headers = ["ID", "Дата", "Имя", "Цена"]
        else:
            headers = ["ID", "Date", "Name", "Price"]

        ws.append(headers)

        # Данные
        for p in queryset:
            price = p.with_discount if p.with_discount else p.service_type.price
            ws.append([
                p.id,
                p.appointment_date.strftime('%d-%m-%Y %H:%M'),
                p.name,
                price,
            ])

        # Итоговая строка с суммой
        total_price = sum(
            p.with_discount if p.with_discount else p.service_type.price
            for p in queryset
        )
        ws.append([])
        ws.append([_("Total"), "", "", total_price])

        # Ответ с Excel
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        filename = self.request.query_params.get('filename', 'report_doctor.xlsx')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        wb.save(response)
        return response


class ReportExactAPIView(generics.ListAPIView):
    """
    Возвращает список пациентов, отфильтрованных по:
    - doctor (id доктора, опционально)
    - department (id департамента, опционально)
    - date (YYYY-MM-DD, опционально)

    Если передан параметр export=excel, возвращается Excel-файл.
    """
    serializer_class = ReportExactSerializer

    def get_queryset(self):
        qs = Patient.objects.select_related("service_type", "doctor")

        doctor_id = self.request.query_params.get('doctor')
        department_id = self.request.query_params.get('department')
        date_str = self.request.query_params.get('date')

        if doctor_id:
            qs = qs.filter(doctor_id=doctor_id)
        if department_id:
            qs = qs.filter(department_id=department_id)
        if date_str:
            selected_date = parse_date(date_str)
            if not selected_date:
                raise ValidationError({"date": "Invalid date format, use YYYY-MM-DD"})
            qs = qs.filter(appointment_date__date=selected_date)

        return qs

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # --- Если экспорт в Excel ---
        if request.query_params.get("export") == "excel":
            return self.export_to_excel(queryset)

        # --- Подсчёты ---
        sum_discount = queryset.aggregate(
            total=Coalesce(Sum('with_discount', filter=Q(with_discount__isnull=False)), Value(0))
        )['total']

        sum_no_discount = queryset.aggregate(
            total=Coalesce(
                Sum('service_type__price', filter=Q(with_discount__isnull=True)),
                Value(0)
            )
        )['total']

        doctor_earnings = 0
        for patient in queryset:
            price = patient.with_discount if patient.with_discount else patient.service_type.price
            percent = patient.doctor.bonus or 0
            doctor_earnings += price * percent / 100

        patients_count = queryset.count()

        payments = queryset.aggregate(
            total_cash=Coalesce(
                Sum(
                    Case(
                        When(payment_type='cash',
                             then=Case(
                                 When(with_discount__isnull=False, then=F('with_discount')),
                                 default=F('service_type__price'),
                                 output_field=IntegerField()
                             )
                             ),
                        default=Value(0),
                        output_field=IntegerField()
                    )
                ),
                Value(0)
            ),
            total_card=Coalesce(
                Sum(
                    Case(
                        When(payment_type='card',
                             then=Case(
                                 When(with_discount__isnull=False, then=F('with_discount')),
                                 default=F('service_type__price'),
                                 output_field=IntegerField()
                             )
                             ),
                        default=Value(0),
                        output_field=IntegerField()
                    )
                ),
                Value(0)
            )
        )

        serializer = self.get_serializer(queryset, many=True)

        return Response({
            "sum_discount": sum_discount,
            "sum_no_discount": sum_no_discount,
            "doctor_earnings": round(doctor_earnings, 2),
            "patients_count": patients_count,
            "total_cash": payments['total_cash'],
            "total_card": payments['total_card'],
            "patients": serializer.data
        })

    def export_to_excel(self, queryset):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Patients"

        # Заголовки по языку
        lang = self.request.LANGUAGE_CODE
        if lang == 'ru':
            headers = [
                "ID", "Дата", "Имя", "Услуга",
                "Тип оплаты", "Цена", "Скидка", "Доктор"
            ]
        else:
            headers = [
                "ID", "Date", "Name", "Service",
                "Payment type", "Price", "Discount", "Doctor"
            ]
        ws.append(headers)

        # Данные
        for p in queryset:
            price = p.with_discount if p.with_discount else p.service_type.price
            ws.append([
                p.id,
                p.appointment_date.strftime('%d-%m-%Y %H:%M'),
                p.name,
                p.service_type.type,
                p.get_payment_type_display(),
                p.service_type.price if p.with_discount is None else "-",
                p.with_discount if p.with_discount else "-",
                p.doctor.username,
            ])

        # Итоговая строка с количеством и суммой
        total_price = sum(
            p.with_discount if p.with_discount else p.service_type.price
            for p in queryset
        )
        ws.append([])
        ws.append([_("Total patients"), queryset.count()])
        ws.append([_("Total amount"), total_price])

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        filename = self.request.query_params.get('filename', 'report_exact.xlsx')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        wb.save(response)
        return response


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


