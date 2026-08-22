from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from core.permissions import IsAdminOrHR, IsAdmin
from .models import Payroll
from .serializers import PayrollSerializer, GeneratePayrollSerializer
from . import services


class PayrollListView(generics.ListAPIView):
    serializer_class = PayrollSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Payroll.objects.select_related('employee__user').all()
        if user.role not in ('admin', 'hr'):
            qs = qs.filter(employee__user=user)
        month = self.request.query_params.get('month')
        year = self.request.query_params.get('year')
        if month:
            qs = qs.filter(month=month)
        if year:
            qs = qs.filter(year=year)
        return qs


class PayrollDetailView(generics.RetrieveUpdateAPIView):
    queryset = Payroll.objects.all()
    serializer_class = PayrollSerializer

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH'):
            return [IsAdmin()]
        return [IsAuthenticated()]


@api_view(['POST'])
@permission_classes([IsAdmin])
def generate_payroll_view(request):
    serializer = GeneratePayrollSerializer(data=request.data)
    if serializer.is_valid():
        payroll, error = services.generate_payroll(
            serializer.validated_data['employee_id'],
            serializer.validated_data['month'],
            serializer.validated_data['year'],
            request.user,
        )
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
        return Response(PayrollSerializer(payroll).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_payroll_view(request):
    qs = Payroll.objects.filter(employee__user=request.user).order_by('-year', '-month')
    return Response(PayrollSerializer(qs, many=True).data)


@api_view(['POST'])
@permission_classes([IsAdmin])
def generate_payroll_bulk_view(request):
    """Generate payroll for ALL active employees with a salary structure for the given month/year."""
    month = request.data.get('month')
    year  = request.data.get('year')
    if not month or not year:
        return Response({'error': 'month and year are required.'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        month, year = int(month), int(year)
    except (TypeError, ValueError):
        return Response({'error': 'month and year must be integers.'}, status=status.HTTP_400_BAD_REQUEST)

    from apps.employees.models import EmployeeProfile, SalaryStructure
    profiles = EmployeeProfile.objects.filter(
        employment_status='active',
        salary_structure__isnull=False
    ).distinct()

    success, skipped, errors = [], [], []
    for profile in profiles:
        payroll, error = services.generate_payroll(profile.pk, month, year, request.user)
        if error:
            skipped.append({'employee': profile.full_name, 'reason': error})
        else:
            success.append({'employee': profile.full_name, 'net_salary': float(payroll.net_salary)})

    return Response({
        'month': month, 'year': year,
        'generated': len(success), 'skipped': len(skipped),
        'results': success, 'skipped_details': skipped,
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAdmin])
def mark_payroll_paid_view(request, pk):
    """Mark a payroll record as paid."""
    try:
        payroll = Payroll.objects.get(pk=pk)
    except Payroll.DoesNotExist:
        return Response({'error': 'Payroll not found.'}, status=status.HTTP_404_NOT_FOUND)
    if payroll.status == 'paid':
        return Response({'error': 'Already marked as paid.'}, status=status.HTTP_400_BAD_REQUEST)
    payroll.status = 'paid'
    payroll.save(update_fields=['status'])
    # Notify employee
    from apps.notifications.services import create_notification
    create_notification(
        recipient=payroll.employee.user,
        notification_type='general',
        title='Salary Credited',
        message=f'Your salary for {payroll.month}/{payroll.year} (Net: ₹{payroll.net_salary}) has been processed.',
        action_url='/payroll/',
    )
    return Response({'message': 'Payroll marked as paid.', 'payroll': PayrollSerializer(payroll).data})
