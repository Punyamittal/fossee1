"""
API client for Chemical Equipment backend.
"""
import os
import requests

API_BASE = os.environ.get('API_BASE', 'http://localhost:8000/api')


class ApiClient:
    def __init__(self, base_url=None):
        self.base = base_url or API_BASE
        self.token = None

    def set_token(self, token):
        self.token = token

    def _headers(self):
        h = {'Content-Type': 'application/json'}
        if self.token:
            h['Authorization'] = f'Bearer {self.token}'
        return h

    def login(self, username, password):
        r = requests.post(
            f'{self.base}/auth/login/',
            json={'username': username, 'password': password},
        )
        r.raise_for_status()
        data = r.json()
        self.set_token(data.get('access'))
        return data

    def register(self, username, password, email=''):
        r = requests.post(
            f'{self.base}/auth/register/',
            json={'username': username, 'password': password, 'email': email},
        )
        r.raise_for_status()
        data = r.json()
        self.set_token(data.get('access'))
        return data

    def upload_csv(self, filepath):
        with open(filepath, 'rb') as f:
            r = requests.post(
                f'{self.base}/upload/',
                files={'file': (os.path.basename(filepath), f, 'text/csv')},
                headers={'Authorization': f'Bearer {self.token}'} if self.token else {},
            )
        r.raise_for_status()
        return r.json()

    def get_datasets(self):
        r = requests.get(f'{self.base}/datasets/', headers=self._headers())
        r.raise_for_status()
        return r.json()

    def get_dataset(self, dataset_id):
        r = requests.get(f'{self.base}/datasets/{dataset_id}/', headers=self._headers())
        r.raise_for_status()
        return r.json()

    def get_summary(self, dataset_id):
        r = requests.get(f'{self.base}/datasets/{dataset_id}/summary/', headers=self._headers())
        r.raise_for_status()
        return r.json()

    def get_equipment(self, dataset_id, page=1):
        r = requests.get(
            f'{self.base}/datasets/{dataset_id}/equipment/?page={page}',
            headers=self._headers(),
        )
        r.raise_for_status()
        return r.json()

    def generate_pdf(self, dataset_id):
        r = requests.post(
            f'{self.base}/datasets/{dataset_id}/generate-pdf/',
            headers=self._headers(),
            stream=True,
        )
        if r.status_code != 200:
            try:
                err = r.json().get('error', r.text)
            except Exception:
                err = r.text or f'HTTP {r.status_code}'
            raise RuntimeError(err)
        return r.content
