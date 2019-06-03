from rest_framework.authtoken.models import Token
from rest_framework.test import APITransactionTestCase

from Tick_server.models import *
from Tick_server.responses import *


class CustomerCredentialTest(APITransactionTestCase):

    def setUp(self) -> None:
        self.phone_number = '09130172688'
        self.code = '1111'

    def __signup_first__(self):
        response = self.client.post('/signup-customer/phone-auth/', {
            'phone_number': self.phone_number
        })
        return response

    def __signup_second__(self):
        response = self.client.post('/signup-customer/confirm-phone/', {
            'phone_number': self.phone_number,
            'code': self.code
        })
        return response

    def __signup_final__(self):
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
        self.assertEqual(Code4Digit.objects.filter(phone_number = self.phone_number).count(), 1)

    def test_unit_signup_second(self):
        Code4Digit.objects.create(phone_number = self.phone_number, code = self.code)
        response = self.client.post('/signup-customer/confirm-phone/', {
            'phone_number': '09223878988',
            'code': '1111'
        })
        self.assertEqual(response.data, customer_code_incorrect)
        response = self.client.post('/signup-customer/confirm-phone/', {
            'phone_number': '09130172688',
            'code': '1234'
        })
        self.assertEqual(response.data, customer_code_incorrect)
        response = self.__signup_second__()
        self.assertEqual(response.data, customer_signup_successful)

    def test_unit_signup_final(self):
        Code4Digit.objects.create(phone_number = self.phone_number, code = self.code)
        City.objects.create(name = 'اصفهان')
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
        user = CustomUser.objects.filter(phone_number = '09130172688', birth_date = '1998-05-04', gender = 'm',
                                         location = '32.615878, 51.618149', city = 1, username = 'mohamadhassan98',
                                         email = 'emohamadhassan@gmail.com')
        self.assertEqual(user.count(), 1)
        self.assertEqual(user[0].check_password('123456'), True)
        self.assertEqual(Customer.objects.filter(user = user[0]).count(), 1)

    def test_unit_resend_code(self):
        self.__signup_first__()
        response = self.client.post('/signup-customer/resend-code/', {
            'phone_number': '09130172688'
        })
        self.assertEqual(response.data, customer_code_resent)
        self.__signup_first__()
        response = self.client.post('/signup-customer/resend-code/', {
            'phone_number': '09130172689'
        })
        self.assertEqual(response.data, customer_code_resend_failed)

    def test_unit_login(self):
        self.__signup_first__()
        self.__signup_second__()
        self.__signup_final__()
        response = self.client.post('/login-customer/', {
            'phone_number': '09130172688',
            'password': '123456'
        })
        result = customer_login_successful.copy()
        # FIXME('Do it together')
        # result.update({
        #     'phone_number': '09130172688',
        #     ''
        # })
        # self.assertEqual(response.data, )

    def test_temp(self):
        customer = Customer()
        user = CustomUser.objects.create(username = 'ali', password = '123456789', phone_number = '09876543210',
                                         email = 'qwerty@azerty.asd')
        customer.user = user
        customer.save()
        customer = Customer()
        user = CustomUser.objects.create(username = 'hassan', password = '123456789', phone_number = '09876543210',
                                         email = 'qwerty@azerty.asd')
        customer.user = user
        customer.save()
