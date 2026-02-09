"""
API tests for Chemical Equipment Parameter Visualizer.
"""
from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from rest_framework import status
from .models import Dataset, Equipment, EquipmentTypeSummary


SAMPLE_CSV = '''Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-A1,Centrifugal Pump,120.5,8.2,65.3
Reactor-B2,Batch Reactor,85.0,15.5,180.0
Heat-Exchanger-C3,Shell and Tube,200.3,6.8,90.5
'''


class UploadAPITest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_upload_csv_success(self):
        f = SimpleUploadedFile('test.csv', SAMPLE_CSV.encode(), content_type='text/csv')
        response = self.client.post('/api/upload/', {'file': f}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertIn('dataset_id', data)
        self.assertEqual(data['total_equipment_count'], 3)
        self.assertEqual(Dataset.objects.count(), 1)
        self.assertEqual(Equipment.objects.count(), 3)

    def test_upload_csv_missing_columns(self):
        f = SimpleUploadedFile('bad.csv', b'Name,Value\nx,1', content_type='text/csv')
        response = self.client.post('/api/upload/', {'file': f}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.json())

    def test_upload_duplicate_rejected(self):
        content = SAMPLE_CSV.encode()
        f1 = SimpleUploadedFile('dup1.csv', content, content_type='text/csv')
        self.client.post('/api/upload/', {'file': f1}, format='multipart')
        f2 = SimpleUploadedFile('dup2.csv', content, content_type='text/csv')
        response = self.client.post('/api/upload/', {'file': f2}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Duplicate', response.json().get('error', ''))


class DatasetsAPITest(TestCase):
    def setUp(self):
        self.client = Client()
        self.dataset = Dataset.objects.create(
            filename='test.csv',
            file_hash='abc123',
            total_equipment_count=2,
        )

    def test_list_datasets(self):
        response = self.client.get('/api/datasets/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)

    def test_dataset_detail(self):
        response = self.client.get(f'/api/datasets/{self.dataset.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['id'], self.dataset.id)
        self.assertEqual(data['filename'], 'test.csv')

    def test_dataset_summary(self):
        response = self.client.get(f'/api/datasets/{self.dataset.id}/summary/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('total_count', data)
        self.assertIn('equipment_type_distribution', data)


class AuthAPITest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@test.com', 'testpass123')

    def test_login_success(self):
        response = self.client.post(
            '/api/auth/login/',
            {'username': 'testuser', 'password': 'testpass123'},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('access', data)
        self.assertIn('refresh', data)

    def test_login_invalid(self):
        response = self.client.post(
            '/api/auth/login/',
            {'username': 'testuser', 'password': 'wrong'},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_register(self):
        response = self.client.post(
            '/api/auth/register/',
            {'username': 'newuser', 'password': 'newpass123'},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())
