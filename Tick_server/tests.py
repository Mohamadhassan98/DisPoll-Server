from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITransactionTestCase

from Tick_server.models import *
from Tick_server.responses import *
from Tick_server.serializers import UserSerializer


class CustomerCredentialTest(APITransactionTestCase):

    def setUp(self) -> None:
        City.objects.create(name = 'اصفهان')
        City.objects.create(name = 'شیراز')
        City.objects.create(name = 'تهران')
        City.objects.create(name = 'یزد')
        City.objects.create(name = 'مشهد')
        ShopKind.objects.create(name = 'مواد غذایی')
        ShopKind.objects.create(name = 'پوشاک')
        ShopKind.objects.create(name = 'آرایشی بهداشتی')
        ShopKind.objects.create(name = 'لوازم التحریر')
        ShopKind.objects.create(name = 'هتل')
        user = CustomUser.objects.create_superuser(username = 'admin', email = 'emohamadhassan@gmail.com',
                                                   password = 'admin')
        Token.objects.create(user = user, key = 'd225d74e7447c5dc66e2845fdd23d0b02be3ba4f')
        self.phone_number = '09130172688'
        self.code = '1111'
        self.username = 'mohamadhassan98'
        self.password = '123456'
        self.admin_key = 'd225d74e7447c5dc66e2845fdd23d0b02be3ba4f'
        self.user_data = {
            'phone_number': '09130172688',
            'birth_date': '1998-05-04',
            'gender': 'm',
            'location': '32.615878, 51.618149',
            'city': '1',
            'username': 'mohamadhassan98',
            'email': 'emohamadhassan@gmail.com',
        }

    def __set_valid_token__(self):
        self.client.credentials(HTTP_AUTHORIZATION = 'Token ' + self.admin_key)

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
            'phone_number': self.phone_number,
            'birth_date': '1998-05-04',
            'gender': 'm',
            'location': '32.615878, 51.618149',
            'city': '1',
            'username': self.username,
            'email': 'emohamadhassan@gmail.com',
            'password': self.password
        })
        return response

    # ####Unit tests################################################################################################## #
    def test_unit_signup_first(self):
        response = self.__signup_first__()
        self.assertEqual(response.data, {'detail': ErrorDetail(string = 'Authentication credentials were not provided.',
                                                               code = 'not_authenticated')})
        self.client.credentials(HTTP_AUTHORIZATION = 'Token ' + 'd225d74e7447d5dc66e2845fdd23d0b02be3ba4f')
        response = self.__signup_first__()
        self.assertEqual(response.data, {"detail": "Invalid token."})
        self.__set_valid_token__()
        response = self.__signup_first__()
        self.assertEqual(response.data, phone_added_successfully)
        self.assertEqual(Code4Digit.objects.filter(phone_number = self.phone_number).count(), 1)

    def test_unit_signup_second(self):
        response = self.__signup_second__()
        self.assertEqual(response.data, {'detail': ErrorDetail(string = 'Authentication credentials were not provided.',
                                                               code = 'not_authenticated')})
        self.client.credentials(HTTP_AUTHORIZATION = 'Token ' + 'd225d74e7447d5dc66e2845fdd23d0b02be3ba4f')
        response = self.__signup_second__()
        self.assertEqual(response.data, {"detail": "Invalid token."})
        self.__set_valid_token__()
        Code4Digit.objects.create(phone_number = self.phone_number, code = self.code)
        response = self.client.post('/signup-customer/confirm-phone/', {
            'phone_number': '09223878988',
            'code': self.code
        })
        self.assertEqual(response.data, customer_code_incorrect)
        response = self.client.post('/signup-customer/confirm-phone/', {
            'phone_number': self.phone_number,
            'code': '1234'
        })
        self.assertEqual(response.data, customer_code_incorrect)
        response = self.__signup_second__()
        self.assertEqual(response.data, customer_signup_successful)

    def test_unit_signup_final(self):
        Code4Digit.objects.create(phone_number = self.phone_number, code = self.code)
        response = self.__signup_final__()
        self.assertEqual(response.data, {'detail': ErrorDetail(string = 'Authentication credentials were not provided.',
                                                               code = 'not_authenticated')})
        self.client.credentials(HTTP_AUTHORIZATION = 'Token ' + 'd225d74e7447d5dc66e2845fdd23d0b02be3ba4f')
        response = self.__signup_final__()
        self.assertEqual(response.data, {"detail": "Invalid token."})
        self.__set_valid_token__()
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
            'city': '12',
            'username': 'mohamadhassan98',
            'email': 'emohamadhassan@gmail.com',
            'password': '123456'
        })
        self.assertEqual(response.data, customer_signup_failed)
        response = self.client.post('/signup-customer/complete-info/', self.user_data)
        self.assertEqual(response.data, customer_signup_failed)
        response = self.__signup_final__()
        token, _ = Token.objects.get_or_create(user = CustomUser.objects.get(phone_number = self.phone_number))
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
        UserSerializer(data = self.user_data)
        Customer
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
