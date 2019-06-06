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
                                                   password = 'admin', phone_number = 'Admin')
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
            'password': '123456',
            'first_name': 'Mohamadhassan',
            'last_name': 'Ebrahimi'
        }
        self.not_authenticated = {'detail': ErrorDetail(string = 'Authentication credentials were not provided.',
                                                        code = 'not_authenticated')}

    def __signup_first__(self):
        response = self.client.post('/customer/signup/phone-auth/', {
            'phone_number': self.phone_number
        })
        return response

    def __signup_second__(self):
        response = self.client.post('/customer/signup/confirm-phone/', {
            'phone_number': self.phone_number,
            'code': self.code
        })
        return response

    def __signup_final__(self):
        response = self.client.post('/customer/signup/complete-info/', self.user_data)
        return response

    def __resend_code__(self):
        response = self.client.post('/customer/signup/resend-code/', {
            'phone_number': '09130172688'
        })
        return response

    def __login__(self):
        response = self.client.post('/customer/login/', {
            'phone_number': self.phone_number,
            'password': self.password
        })
        return response

    def __edit_normal_user_profile__(self):
        response = self.client.post('/customer/edit-profile/', {
            'phone_number': self.phone_number,
            'first_name': 'Mohammadhasan'
        })
        return response

    def __edit_anonymous_user_profile__(self):
        response = self.client.post('/customer/edit-profile/', {
            'phone_number': '09223878988',
            'first_name': 'Glare',
            'old_password': '123456',
            'password': '123456789'
        })
        return response

    def __set_valid_token__(self):
        self.client.credentials(HTTP_AUTHORIZATION = 'Token ' + self.admin_key)

    def __reset_token__(self):
        self.client.credentials(HTTP_AUTHORIZATION = '')

    def __set_invalid_token__(self):
        self.client.credentials(HTTP_AUTHORIZATION = 'Token df')

    # noinspection PyMethodMayBeStatic
    def __add_anonymous_user__(self):
        user = CustomUser.objects.create_user(username = 'glare', password = '123456', user_type = 'CU',
                                              phone_number = '09223878988')
        Customer.objects.create(user = user)
        token, _ = Token.objects.get_or_create(user = user)
        return str(token)

    def __add_normal_user__(self):
        data = self.user_data.copy()
        data.update({'user_type': 'CU'})
        serializer = UserSerializer(data = data)
        serializer.is_valid()
        user = serializer.save()
        Customer.objects.create(user = user)
        token, _ = Token.objects.get_or_create(user = user)
        return str(token)

    # ####Unit tests################################################################################################## #
    def test_unit_signup_first(self):
        response = self.__signup_first__()
        self.assertEqual(response.data, self.not_authenticated)
        self.__set_invalid_token__()
        response = self.__signup_first__()
        self.assertEqual(response.data, {"detail": "Invalid token."})
        self.__set_valid_token__()
        response = self.client.post('/customer/signup/phone-auth/', {
            'phone': self.phone_number
        })
        self.assertEqual(response.data, insufficient_data)
        response = self.__signup_first__()
        self.assertEqual(response.data, phone_added_successfully)
        self.assertEqual(Code4Digit.objects.filter(phone_number = self.phone_number).count(), 1)
        self.client.credentials(HTTP_AUTHORIZATION = 'Token ' + self.__add_anonymous_user__())
        response = self.__signup_first__()
        self.assertEqual(response.data, access_denied)
        self.__set_valid_token__()
        response = self.client.post('/customer/signup/phone-auth/', {
            'phone_number': '09223878988'
        })
        self.assertEqual(response.data, customer_already_exists)
        self.__reset_token__()

    def test_unit_signup_second(self):
        response = self.__signup_second__()
        self.assertEqual(response.data, self.not_authenticated)
        self.__set_invalid_token__()
        response = self.__signup_second__()
        self.assertEqual(response.data, {"detail": "Invalid token."})
        Code4Digit.objects.create(phone_number = self.phone_number, code = self.code)
        self.client.credentials(HTTP_AUTHORIZATION = 'Token ' + self.__add_anonymous_user__())
        response = self.__signup_second__()
        self.assertEqual(response.data, access_denied)
        self.__set_valid_token__()
        response = self.client.post('/customer/signup/confirm-phone/', {
            'phone': self.phone_number,
            'code': self.code
        })
        self.assertEqual(response.data, insufficient_data)
        response = self.client.post('/customer/signup/confirm-phone/', {
            'phone_number': '09223878988',
            'code': self.code
        })
        self.assertEqual(response.data, code_incorrect)
        response = self.client.post('/customer/signup/confirm-phone/', {
            'phone_number': self.phone_number,
            'code': '1234'
        })
        self.assertEqual(response.data, code_incorrect)
        response = self.__signup_second__()
        self.assertEqual(response.data, signup_successful)
        self.__reset_token__()

    def test_unit_signup_final(self):
        Code4Digit.objects.create(phone_number = self.phone_number, code = self.code)
        response = self.__signup_final__()
        self.assertEqual(response.data, self.not_authenticated)
        self.__set_invalid_token__()
        response = self.__signup_final__()
        self.assertEqual(response.data, {"detail": "Invalid token."})
        self.client.credentials(HTTP_AUTHORIZATION = 'Token ' + self.__add_anonymous_user__())
        response = self.__signup_final__()
        self.assertEqual(response.data, access_denied)
        self.__set_valid_token__()
        response = self.client.post('/customer/signup/complete-info/', {
            'phone': '09130172688',
            'birth_date': '1998-05-04',
            'gender': 'm',
            'location': '32.615878, 51.618149',
            'city': '1',
            'username': 'mohamadhassan98',
            'email': 'emohamadhassan@gmail.com',
            'password': '123456',
            'first_name': 'Mohamadhassan',
            'last_name': 'Ebrahimi'
        })
        self.assertEqual(response.data, insufficient_data)
        response = self.client.post('/customer/signup/complete-info/', {
            'phone_number': '09130172687',
            'birth_date': '1998/05/04',
            'gender': 'male',
            'location': '32.615878, 51.618149',
            'city': '12',
            'username': 'mohamadhassan98',
            'email': 'emohamadhassan@gmail.com',
        })
        self.assertEqual(response.data, signup_failed)
        response = self.__signup_final__()
        token, _ = Token.objects.get_or_create(user = CustomUser.objects.get(phone_number = self.phone_number))
        result = signup_successful.copy()
        result.update({'token': token.key})
        self.assertEqual(response.data, result)
        user = CustomUser.objects.filter(phone_number = '09130172688', birth_date = '1998-05-04', gender = 'm',
                                         location = '32.615878, 51.618149', city = 1, username = 'mohamadhassan98',
                                         email = 'emohamadhassan@gmail.com')
        self.assertEqual(user.count(), 1)
        self.assertEqual(user[0].check_password('123456'), True)
        self.assertEqual(Customer.objects.filter(user = user[0]).count(), 1)
        self.__reset_token__()

    def test_unit_resend_code(self):
        Code4Digit.objects.create(phone_number = self.phone_number, code = self.code)
        response = self.__resend_code__()
        self.assertEqual(response.data, self.not_authenticated)
        self.__set_invalid_token__()
        response = self.__resend_code__()
        self.assertEqual(response.data, {"detail": "Invalid token."})
        self.client.credentials(HTTP_AUTHORIZATION = 'Token ' + self.__add_anonymous_user__())
        response = self.__resend_code__()
        self.assertEqual(response.data, access_denied)
        self.__set_valid_token__()
        response = self.client.post('/customer/signup/resend-code/', {
            'phone': self.phone_number
        })
        self.assertEqual(response.data, insufficient_data)
        response = self.client.post('/customer/signup/resend-code/', {
            'phone_number': '09130172689'
        })
        self.assertEqual(response.data, customer_code_resend_failed)
        response = self.__resend_code__()
        self.assertEqual(response.data, code_resent)
        self.__signup_first__()
        self.__reset_token__()

    # noinspection PyTypeChecker
    def test_unit_login(self):
        token = self.__add_normal_user__()
        response = self.__login__()
        self.assertEqual(response.data, self.not_authenticated)
        self.__set_invalid_token__()
        response = self.__login__()
        self.assertEqual(response.data, {"detail": "Invalid token."})
        self.client.credentials(HTTP_AUTHORIZATION = 'Token ' + self.__add_anonymous_user__())
        response = self.__login__()
        self.assertEqual(response.data, access_denied)
        self.__set_valid_token__()
        response = self.client.post('/customer/login/', {
            'phone': self.phone_number,
            'password': self.password
        })
        self.assertEqual(response.data, insufficient_data)
        response = self.client.post('/customer/login/', {
            'phone_number': '09131674340',
            'password': self.password
        })
        self.assertEqual(response.data, customer_not_found)
        response = self.client.post('/customer/login/', {
            'phone_number': self.phone_number,
            'password': '122122'
        })
        self.assertEqual(response.data, customer_wrong_password)
        response = self.__login__()
        result = customer_login_successful.copy()
        user_data = self.user_data.copy()
        user_data.pop('password')
        city = int(self.user_data['city'])
        user_data.update({'city': city})
        result.update({'customer_info': user_data})
        result.update({'token': token})
        self.maxDiff = None
        self.assertEqual(response.data, result)
        self.__reset_token__()

    def test_edit_profile(self):
        token1 = self.__add_normal_user__()
        token2 = self.__add_anonymous_user__()
        response = self.__edit_normal_user_profile__()
        self.assertEqual(response.data, self.not_authenticated)
        self.__set_invalid_token__()
        response = self.__edit_normal_user_profile__()
        self.assertEqual(response.data, {"detail": "Invalid token."})
        self.client.credentials(HTTP_AUTHORIZATION = 'Token ' + token2)
        response = self.__edit_normal_user_profile__()
        self.assertEqual(response.data, access_denied)
        self.__set_valid_token__()
        response = self.client.post('/customer/edit-profile/', {
            'phone_number': 'Admin'
        })
        self.assertEqual(response.data, access_denied)
        self.client.credentials(HTTP_AUTHORIZATION = 'Token ' + token1)
        response = self.client.post('/customer/edit-profile/', {
            'phone_number': self.phone_number,
            'email': 'email'
        })
        self.assertEqual(response.data, customer_edit_profile_failed)
        response = self.__edit_normal_user_profile__()
        self.assertEqual(response.data, customer_edit_profile_successful)
        user = CustomUser.objects.get(phone_number = self.phone_number)
        self.assertEqual(user.first_name, 'Mohammadhasan')
        self.client.credentials(HTTP_AUTHORIZATION = 'Token ' + token2)
        response = self.client.post('/customer/edit-profile/', {
            'phone_number': '09223878988',
            'old_password': '654321'
        })
        self.assertEqual(response.data, customer_wrong_old_password)
        response = self.__edit_anonymous_user_profile__()
        self.assertEqual(response.data, customer_edit_profile_successful)
        self.assertEqual(CustomUser.objects.get(phone_number = '09223878988').check_password('123456789'), True)
