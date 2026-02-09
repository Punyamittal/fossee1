"""
Models for Chemical Equipment Parameter Visualizer.
"""
import hashlib
from decimal import Decimal
from django.db import models
from django.conf import settings


class Dataset(models.Model):
    """Stores metadata for uploaded CSV datasets."""
    filename = models.CharField(max_length=255)
    upload_timestamp = models.DateTimeField(auto_now_add=True)
    total_equipment_count = models.IntegerField(default=0)
    avg_flowrate = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    avg_pressure = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    avg_temperature = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    file_hash = models.CharField(max_length=64, unique=True, db_index=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='datasets'
    )

    class Meta:
        ordering = ['-upload_timestamp']
        indexes = [
            models.Index(fields=['upload_timestamp']),
        ]

    def __str__(self):
        return f"{self.filename} ({self.upload_timestamp})"


class Equipment(models.Model):
    """Individual equipment records from a dataset."""
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='equipment_list', db_index=True)
    equipment_name = models.CharField(max_length=255)
    equipment_type = models.CharField(max_length=100, db_index=True)
    flowrate = models.DecimalField(max_digits=12, decimal_places=2)
    pressure = models.DecimalField(max_digits=12, decimal_places=2)
    temperature = models.DecimalField(max_digits=12, decimal_places=2)
    row_number = models.IntegerField(default=0)

    class Meta:
        ordering = ['row_number']
        indexes = [
            models.Index(fields=['dataset_id', 'equipment_type']),
        ]
        verbose_name_plural = 'Equipment'

    def __str__(self):
        return f"{self.equipment_name} ({self.equipment_type})"


class EquipmentTypeSummary(models.Model):
    """Aggregated stats per equipment type per dataset."""
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='type_summaries', db_index=True)
    equipment_type = models.CharField(max_length=100, db_index=True)
    count = models.IntegerField(default=0)
    avg_flowrate = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    avg_pressure = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    avg_temperature = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    min_flowrate = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    max_flowrate = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    min_pressure = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    max_pressure = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    min_temperature = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    max_temperature = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ['equipment_type']
        indexes = [
            models.Index(fields=['dataset_id', 'equipment_type']),
        ]
        verbose_name_plural = 'Equipment type summaries'


class PDFReport(models.Model):
    """Generated PDF reports for datasets."""
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='reports', db_index=True)
    report_filename = models.CharField(max_length=255)
    generated_at = models.DateTimeField(auto_now_add=True)
    file_path = models.CharField(max_length=500)
    file_size = models.BigIntegerField(default=0)

    def __str__(self):
        return f"{self.report_filename} for dataset {self.dataset_id}"


def compute_file_hash(content_bytes):
    """Compute SHA256 hash of file content for duplicate detection."""
    return hashlib.sha256(content_bytes).hexdigest()
