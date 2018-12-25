import requests

from django.test import TestCase

class LoginTest(TestCase):
    def setUp(self):
        self.base_url = 'http://localhost:8000/{}'
        self.valid_phone_number = '09195379743'
        self.invalid_phone_number = '0912'
        self.password = '1023'
        self.invalid_token = ''

    def test_login_invalid(self):
        data = {
            'phone_number': self.invalid_phone_number,
        }
        response = requests.post(url=self.base_url.format('accounts/login/'), data=data)
        self.assertEqual(response.status_code, 400)

    def test_invalid_confirmation(self):
        bad_data = {
            'phone_number': self.valid_phone_number,
        }
        response = requests.post(url=self.base_url.format('accounts/confirmation/'), data=bad_data)
        self.assertEqual(response.status_code, 400)

    def test_authorization(self):
        headers = {
            'Authorization': "Bearer {}".format(self.invalid_token),
        }
        response = requests.get(url=self.base_url.format('accounts/test/'), headers=headers)
        self.assertEqual(response.status_code, 401)
