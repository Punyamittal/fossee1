"""
API views for Chemical Equipment Parameter Visualizer.
"""
import io
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.http import FileResponse, Http404, HttpResponse
from django.conf import settings

from .models import Dataset, Equipment, EquipmentTypeSummary, PDFReport
from .serializers import DatasetListSerializer, DatasetDetailSerializer, EquipmentSerializer, UserSerializer
from .utils import parse_csv_with_pandas, calculate_summary_stats, prune_old_datasets, generate_pdf_report


# Allow unauthenticated for upload/auth to simplify testing; protect other endpoints optionally
def get_permission():
    return [AllowAny()]  # Change to [IsAuthenticated()] for production


@api_view(['POST'])
@permission_classes([AllowAny])
def upload_csv(request):
    """Accept CSV file, validate, parse, save Dataset + Equipment."""
    if 'file' not in request.FILES and 'csv' not in request.FILES:
        return Response(
            {'error': 'No file provided. Use form field "file" or "csv".'},
            status=status.HTTP_400_BAD_REQUEST
        )
    file = request.FILES.get('file') or request.FILES.get('csv')
    content = file.read()
    file_hash = __import__('hashlib').sha256(content).hexdigest()

    if Dataset.objects.filter(file_hash=file_hash).exists():
        return Response(
            {'error': 'Duplicate file. This CSV has already been uploaded.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        df = parse_csv_with_pandas(io.BytesIO(content))
    except ValueError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    summary = calculate_summary_stats(df)
    user = request.user if request.user.is_authenticated else None

    dataset = Dataset.objects.create(
        filename=file.name,
        file_hash=file_hash,
        total_equipment_count=summary['total_count'],
        avg_flowrate=summary['avg_flowrate'],
        avg_pressure=summary['avg_pressure'],
        avg_temperature=summary['avg_temperature'],
        uploaded_by=user,
    )

    # Create equipment records
    for i, row in df.iterrows():
        Equipment.objects.create(
            dataset=dataset,
            equipment_name=str(row['Equipment Name']),
            equipment_type=str(row['Type']),
            flowrate=row['Flowrate'],
            pressure=row['Pressure'],
            temperature=row['Temperature'],
            row_number=int(i) + 1,
        )

    # Create equipment type summaries
    for eq_type, count in summary['equipment_type_distribution'].items():
        subset = df[df['Type'] == eq_type]
        EquipmentTypeSummary.objects.create(
            dataset=dataset,
            equipment_type=eq_type,
            count=count,
            avg_flowrate=subset['Flowrate'].mean(),
            avg_pressure=subset['Pressure'].mean(),
            avg_temperature=subset['Temperature'].mean(),
            min_flowrate=subset['Flowrate'].min(),
            max_flowrate=subset['Flowrate'].max(),
            min_pressure=subset['Pressure'].min(),
            max_pressure=subset['Pressure'].max(),
            min_temperature=subset['Temperature'].min(),
            max_temperature=subset['Temperature'].max(),
        )

    prune_old_datasets()
    return Response({
        'dataset_id': dataset.id,
        'filename': dataset.filename,
        'total_equipment_count': dataset.total_equipment_count,
        'avg_flowrate': float(dataset.avg_flowrate) if dataset.avg_flowrate else None,
        'avg_pressure': float(dataset.avg_pressure) if dataset.avg_pressure else None,
        'avg_temperature': float(dataset.avg_temperature) if dataset.avg_temperature else None,
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([AllowAny])
def dataset_list(request):
    """List last 5 datasets with metadata."""
    datasets = Dataset.objects.all().order_by('-upload_timestamp')[:5]
    serializer = DatasetListSerializer(datasets, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def dataset_detail(request, pk):
    """Get specific dataset with full equipment list."""
    try:
        dataset = Dataset.objects.get(pk=pk)
    except Dataset.DoesNotExist:
        raise Http404
    serializer = DatasetDetailSerializer(dataset)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def dataset_summary(request, pk):
    """Return JSON with total count, averages, type distribution, min/max."""
    try:
        dataset = Dataset.objects.get(pk=pk)
    except Dataset.DoesNotExist:
        raise Http404
    summaries = list(EquipmentTypeSummary.objects.filter(dataset_id=pk))
    type_dist = {s.equipment_type: s.count for s in summaries}

    def _min_val(attr):
        vals = [float(getattr(s, attr)) for s in summaries if getattr(s, attr) is not None]
        return min(vals) if vals else None

    def _max_val(attr):
        vals = [float(getattr(s, attr)) for s in summaries if getattr(s, attr) is not None]
        return max(vals) if vals else None

    data = {
        'total_count': dataset.total_equipment_count,
        'avg_flowrate': float(dataset.avg_flowrate) if dataset.avg_flowrate else None,
        'avg_pressure': float(dataset.avg_pressure) if dataset.avg_pressure else None,
        'avg_temperature': float(dataset.avg_temperature) if dataset.avg_temperature else None,
        'equipment_type_distribution': type_dist,
        'min_flowrate': _min_val('min_flowrate'),
        'max_flowrate': _max_val('max_flowrate'),
        'min_pressure': _min_val('min_pressure'),
        'max_pressure': _max_val('max_pressure'),
        'min_temperature': _min_val('min_temperature'),
        'max_temperature': _max_val('max_temperature'),
    }
    return Response(data)


class EquipmentList(generics.ListAPIView):
    """Paginated list of equipment records for a dataset."""
    serializer_class = EquipmentSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Equipment.objects.filter(dataset_id=self.kwargs['pk']).order_by('row_number')


@api_view(['POST'])
@permission_classes([AllowAny])
def generate_pdf(request, pk):
    """Generate PDF report and return file download."""
    try:
        Dataset.objects.get(pk=pk)
    except Dataset.DoesNotExist:
        raise Http404
    try:
        path = generate_pdf_report(pk)
    except Exception as e:
        import logging
        logging.exception('PDF generation failed')
        return Response(
            {'error': f'PDF generation failed: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    try:
        with open(path, 'rb') as f:
            content = f.read()
        response = HttpResponse(content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="report_dataset_{pk}.pdf"'
        return response
    except Exception as e:
        import logging
        logging.exception('PDF file read failed')
        return Response(
            {'error': f'Could not read PDF: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Auth views
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """User registration."""
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email', '')
    if not username or not password:
        return Response(
            {'error': 'username and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    if User.objects.filter(username=username).exists():
        return Response(
            {'error': 'Username already exists'},
            status=status.HTTP_400_BAD_REQUEST
        )
    user = User.objects.create_user(username=username, password=password, email=email)
    refresh = RefreshToken.for_user(user)
    return Response({
        'user': UserSerializer(user).data,
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """Username + password login, return JWT."""
    from django.contrib.auth import authenticate
    username = request.data.get('username')
    password = request.data.get('password')
    if not username or not password:
        return Response(
            {'error': 'username and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    user = authenticate(username=username, password=password)
    if user is None:
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    refresh = RefreshToken.for_user(user)
    return Response({
        'user': UserSerializer(user).data,
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    })
