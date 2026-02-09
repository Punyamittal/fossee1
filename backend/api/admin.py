from django.contrib import admin
from .models import Dataset, Equipment, EquipmentTypeSummary, PDFReport


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ['id', 'filename', 'upload_timestamp', 'total_equipment_count', 'file_hash']


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'equipment_name', 'equipment_type', 'flowrate', 'pressure', 'temperature', 'dataset_id']
    list_filter = ['equipment_type', 'dataset']


@admin.register(EquipmentTypeSummary)
class EquipmentTypeSummaryAdmin(admin.ModelAdmin):
    list_display = ['id', 'dataset', 'equipment_type', 'count']


@admin.register(PDFReport)
class PDFReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'dataset', 'report_filename', 'generated_at', 'file_size']
