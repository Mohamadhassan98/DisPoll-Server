from rest_framework.test import APITestCase

from Tick_server.models import *
from Tick_server.responses import *


class CustomerCredentialTest(APITestCase):

    def test_scenario(self):
        self.signup_first()
        self.signup_second()

    # ####Unit tests################################################################################################## #
    def test_unit_signup_first(self):
        response = self.client.post('/signup-customer/phone-auth/', {
            'phone_number': '09130172688'
        })
        self.assertEqual(response.data, phone_added_successfully)
        self.assertEqual(Code4Digit.objects.filter(phone_number = '09130172688').count(), 1)

    def test_unit_signup_second(self):
        self.client.post('/signup-customer/phone-auth/', {
            'phone_number': '09130172688'
        })
        response = self.client.post('/signup-customer/confirm-phone/', {
            'phone_number': '09130172688',
            'code': '1111'
        })
        self.assertEqual(response.data, customer_signup_successful)
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


    def signup_final(self):
        data = {

        }
