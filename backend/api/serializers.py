"""
Serializers for Chemical Equipment API.
"""
from rest_framework import serializers
from django.contrib.auth.models import User

from .models import Dataset, Equipment, EquipmentTypeSummary


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = ['id', 'equipment_name', 'equipment_type', 'flowrate', 'pressure', 'temperature', 'row_number']


class EquipmentTypeSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentTypeSummary
        fields = [
            'id', 'equipment_type', 'count',
            'avg_flowrate', 'avg_pressure', 'avg_temperature',
            'min_flowrate', 'max_flowrate', 'min_pressure', 'max_pressure',
            'min_temperature', 'max_temperature',
        ]


class DatasetListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dataset
        fields = ['id', 'filename', 'upload_timestamp', 'total_equipment_count', 'avg_flowrate', 'avg_pressure', 'avg_temperature']


class DatasetDetailSerializer(serializers.ModelSerializer):
    equipment_list = EquipmentSerializer(many=True, read_only=True)
    type_summaries = EquipmentTypeSummarySerializer(many=True, read_only=True)

    class Meta:
        model = Dataset
        fields = [
            'id', 'filename', 'upload_timestamp', 'total_equipment_count',
            'avg_flowrate', 'avg_pressure', 'avg_temperature',
            'equipment_list', 'type_summaries',
        ]
