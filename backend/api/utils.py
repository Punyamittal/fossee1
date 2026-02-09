"""
Utility functions for CSV parsing, analytics, and PDF generation.
"""
import io
import os
from decimal import Decimal
from django.conf import settings
from django.db.models import Count

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image

from .models import Dataset, Equipment, EquipmentTypeSummary, PDFReport


REQUIRED_COLUMNS = ['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']


def parse_csv_with_pandas(file) -> pd.DataFrame:
    """
    Validate and parse CSV file. Raises ValueError on invalid format.
    Returns pandas DataFrame with normalized column names.
    """
    try:
        content = file.read()
        if isinstance(content, bytes):
            content = content.decode('utf-8')
        df = pd.read_csv(io.StringIO(content))
    except Exception as e:
        raise ValueError(f"Invalid CSV format: {str(e)}")

    # Normalize column names (strip whitespace, handle common variants)
    df.columns = df.columns.str.strip()

    # Check required columns (case-insensitive mapping)
    col_map = {c.lower(): c for c in df.columns}
    missing = []
    for req in REQUIRED_COLUMNS:
        if req.lower() not in col_map:
            missing.append(req)

    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}. Found: {', '.join(df.columns)}")

    # Rename to standard names
    rename_map = {col_map[r.lower()]: r for r in REQUIRED_COLUMNS}
    df = df.rename(columns=rename_map)

    # Validate numeric columns
    for col in ['Flowrate', 'Pressure', 'Temperature']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        if df[col].isna().any():
            raise ValueError(f"Column '{col}' contains non-numeric values")

    return df


def calculate_summary_stats(df: pd.DataFrame) -> dict:
    """
    Calculate total count, averages, type distribution, min/max.
    Returns dict suitable for API response.
    """
    total = len(df)
    type_dist = df.groupby('Type').size().to_dict()

    summary = {
        'total_count': total,
        'avg_flowrate': float(df['Flowrate'].mean()) if total > 0 else 0,
        'avg_pressure': float(df['Pressure'].mean()) if total > 0 else 0,
        'avg_temperature': float(df['Temperature'].mean()) if total > 0 else 0,
        'equipment_type_distribution': type_dist,
        'min_flowrate': float(df['Flowrate'].min()) if total > 0 else None,
        'max_flowrate': float(df['Flowrate'].max()) if total > 0 else None,
        'min_pressure': float(df['Pressure'].min()) if total > 0 else None,
        'max_pressure': float(df['Pressure'].max()) if total > 0 else None,
        'min_temperature': float(df['Temperature'].min()) if total > 0 else None,
        'max_temperature': float(df['Temperature'].max()) if total > 0 else None,
    }
    return summary


def prune_old_datasets():
    """
    Delete oldest datasets when count exceeds MAX_DATASETS.
    Uses Django ORM - no DB trigger needed.
    """
    max_ds = getattr(settings, 'MAX_DATASETS', 5)
    ids_to_keep = list(
        Dataset.objects.all().order_by('-upload_timestamp').values_list('id', flat=True)[:max_ds]
    )
    Dataset.objects.exclude(id__in=ids_to_keep).delete()


def generate_pdf_report(dataset_id: int) -> str:
    """
    Generate PDF report with summary + charts.
    Returns path to saved PDF file.
    """
    dataset = Dataset.objects.get(id=dataset_id)
    equipment = list(Equipment.objects.filter(dataset_id=dataset_id).order_by('row_number'))
    type_summaries = list(EquipmentTypeSummary.objects.filter(dataset_id=dataset_id))

    # Ensure media folder exists
    media_dir = settings.MEDIA_ROOT / 'reports'
    media_dir.mkdir(parents=True, exist_ok=True)

    filename = f"report_dataset_{dataset_id}.pdf"
    file_path = media_dir / filename

    doc = SimpleDocTemplate(
        str(file_path),
        pagesize=letter,
        rightMargin=inch,
        leftMargin=inch,
        topMargin=inch,
        bottomMargin=inch,
    )
    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph(f"Equipment Report: {dataset.filename}", styles['Title']))
    elements.append(Paragraph(f"Uploaded: {dataset.upload_timestamp.strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
    elements.append(Spacer(1, 0.3 * inch))

    # Summary table
    elements.append(Paragraph("Summary Statistics", styles['Heading2']))
    summary_data = [
        ['Metric', 'Value'],
        ['Total Equipment Count', str(dataset.total_equipment_count)],
        ['Avg Flowrate', str(dataset.avg_flowrate) if dataset.avg_flowrate else 'N/A'],
        ['Avg Pressure', str(dataset.avg_pressure) if dataset.avg_pressure else 'N/A'],
        ['Avg Temperature', str(dataset.avg_temperature) if dataset.avg_temperature else 'N/A'],
    ]
    t = Table(summary_data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 0.3 * inch))

    # Equipment type distribution
    elements.append(Paragraph("Equipment Type Distribution", styles['Heading2']))
    type_data = [['Type', 'Count']]
    for ts in type_summaries:
        type_data.append([ts.equipment_type, str(ts.count)])
    t2 = Table(type_data)
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(t2)
    elements.append(Spacer(1, 0.3 * inch))

    # Top 5 by flowrate
    elements.append(Paragraph("Top 5 Equipment by Flowrate", styles['Heading2']))
    top5 = sorted(equipment, key=lambda e: float(e.flowrate), reverse=True)[:5]
    top_data = [['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']]
    for e in top5:
        top_data.append([e.equipment_name, e.equipment_type, str(e.flowrate), str(e.pressure), str(e.temperature)])
    t3 = Table(top_data)
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(t3)

    doc.build(elements)

    file_size = os.path.getsize(file_path)
    # Store report record
    PDFReport.objects.update_or_create(
        dataset_id=dataset_id,
        defaults={
            'report_filename': filename,
            'file_path': str(file_path),
            'file_size': file_size,
        }
    )
    return str(file_path)
