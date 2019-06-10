from rest_framework import serializers

from Tick_server.models import *

customer_signup_first = """
{
    "phone_number": "09130172688"
}
"""


class PhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('phone_number',)


phone_added_successfully = """
{
    'result': True,
    'message': 'شماره تلفن با موفقیت ثبت شد.'
}
"""

customer_signup_second = """
{
    "phone_number" : "09130172688",
    "code": "1111"
}
"""

signup_successful = """
{
    'result': True,
    'message': 'ثبت‌نام با موفقیت انجام شد.'
}
"""

code_resent = """
{
    'result': True,
    'message': 'کد مجدداً ارسال شد.'
}
"""

customer_signup_final = """
{
    'phone_number': '09130172688',
    'username': 'Mohamadhassan98',
    'password': 'This_is/A strong ##PASSword!',
    'first_name': 'Mohamadhassan',
    'last_name': 'Ebrahimi',
    'birth_date': '1998-01-11',
    'email': 'emohamadhassan@gmail.com',
    'gender': 'm',
    'location': '32.674507,51.690543',
    'city': '1'
}
"""

signup_successful2 = """
{
    'result': True,
    'message': 'ثبت‌نام با موفقیت انجام شد.',
    'token': 'hdj1nksdjhf4w322jknbkj'
}
"""


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            'username', 'email', 'password', 'birth_date', 'gender', 'location', 'phone_number', 'city', 'first_name',
            'last_name'
        )


class Response(models.Model):
    result = models.BooleanField()
    message = models.CharField(max_length = 100)


class ResponseWithToken(Response):
    token = models.CharField(max_length = 18)


class ResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Response
        exclude = ('id',)


class ResponseWithTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResponseWithToken
        exclude = ('id',)
