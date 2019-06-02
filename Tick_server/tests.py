from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from Tick_server.models import *
from Tick_server.responses import *


class CustomerCredentialTest(APITestCase):

    def test_scenario(self):
        self.__signup_first__()
        self.__signup_second__()

    def __signup_first__(self):
        response = self.client.post('/signup-customer/phone-auth/', {
            'phone_number': '09130172688'
        })
        return response

    def __signup_second__(self):
        response = self.client.post('/signup-customer/confirm-phone/', {
            'phone_number': '09130172688',
            'code': '1111'
        })
        return response

    def __signup_final__(self):
        City.objects.create(name = 'Isfahan')
        response = self.client.post('/signup-customer/complete-info/', {
            'phone_number': '09130172688',
            'birth_date': '1998-05-04',
            'gender': 'm',
            'location': '32.615878, 51.618149',
            'city': '1',
            'username': 'mohamadhassan98',
            'email': 'emohamadhassan@gmail.com',
            'password': '123456'
        })
        return response

    # ####Unit tests################################################################################################## #
    def test_unit_signup_first(self):
        response = self.__signup_first__()
        self.assertEqual(response.data, phone_added_successfully)
        self.assertEqual(Code4Digit.objects.filter(phone_number = '09130172688').count(), 1)

    def test_unit_signup_second(self):
        self.__signup_first__()
        response = self.client.post('/signup-customer/confirm-phone/', {
            'phone_number': '09223878988',
            'code': '1111'
        })
        self.assertEqual(response.data, customer_code_incorrect)
        response = self.client.post('/signup-customer/confirm-phone/', {
            'phone_number': '09223878988',
            'code': '1234'
        })
        self.assertEqual(response.data, customer_code_incorrect)
        response = self.__signup_second__()
        self.assertEqual(response.data, customer_signup_successful)

    def test_unit_signup_final(self):
        self.__signup_first__()
        self.__signup_second__()
        response = self.client.post('/signup-customer/complete-info/', {
            'phone_number': '09130172687',
            'birth_date': '1998-05-04',
            'gender': 'm',
            'location': '32.615878, 51.618149',
            'city': '1',
            'username': 'mohamadhassan98',
            'email': 'emohamadhassan@gmail.com',
            'password': '123456'
        })
        self.assertEqual(response.data, customer_signup_failed)
        response = self.client.post('/signup-customer/complete-info/', {
            'phone_number': '09130172688',
            'birth_date': '1998/05/04',
            'gender': 'm',
            'location': '32.615878, 51.618149',
            'city': '1',
            'username': 'mohamadhassan98',
            'email': 'emohamadhassan@gmail.com',
            'password': '123456'
        })
        self.assertEqual(response.data, customer_signup_failed)
        response = self.client.post('/signup-customer/complete-info/', {
            'phone_number': '09130172688',
            'birth_date': '1998-05-04',
            'gender': 'male',
            'location': '32.615878, 51.618149',
            'city': '1',
            'username': 'mohamadhassan98',
            'email': 'emohamadhassan@gmail.com',
            'password': '123456'
        })
        self.assertEqual(response.data, customer_signup_failed)
        response = self.client.post('/signup-customer/complete-info/', {
            'phone_number': '09130172688',
            'birth_date': '1998-05-04',
            'gender': 'm',
            'location': '32.615878, 51.618149',
            'city': '5',
            'username': 'mohamadhassan98',
            'email': 'emohamadhassan@gmail.com',
            'password': '123456'
        })
        self.assertEqual(response.data, customer_signup_failed)
        response = self.client.post('/signup-customer/complete-info/', {
            'phone_number': '09130172688',
            'birth_date': '1998-05-04',
            'gender': 'm',
            'location': '32.615878, 51.618149',
            'city': '1',
            'username': 'mohamadhassan98',
            'email': 'emohamadhassan@gmail.com',
        })
        self.assertEqual(response.data, customer_signup_failed)
        response = self.__signup_final__()
        token, _ = Token.objects.get_or_create(user = CustomUser.objects.get(pk = 1))
        result = customer_signup_successful.copy()
        result.update({'token': token.key})
        self.assertEqual(response.data, result)



