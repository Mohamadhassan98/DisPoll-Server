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

customer_signup_successful = """
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

customer_signup_successful2 = """
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


class MyResponse(models.Model):
    result = models.BooleanField()
    message = models.CharField(max_length = 100)


class ResponseWithToken(MyResponse):
    token = models.CharField(max_length = 18)


class ResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyResponse
        exclude = ('id',)


class ResponseWithTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResponseWithToken
        exclude = ('id',)


customer_login = """
{
    'phone_number': '09130172688',
    'password': 'This_is/A strong ##PASSword!'
}
"""

customer_login_successful = """
{
    'result': true,
    'message': 'ورود با موفقیت انجام شد.',
    'customer_info': {
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
    'token': 'hdj1nksdjhf4w322jknbkj'
}
"""


class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            'phone_number', 'password'
        )


class ResponseWithUser(ResponseWithToken):
    customer_info = models.OneToOneField(CustomUser, on_delete = models.CASCADE, related_name = 'response')


class ResponseWithUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResponseWithUser
        fields = '__all__'
        depth = 1


customer_edit_pro = """
{
    'old_password': 'This_is/A strong ##PASSword!',
    'password' : 'This_is/A strong ##PASSword!',
    'username': 'Mohamadhassan99'
}
"""

customer_edit_pro_successful = """
{
    'result': True,
    'message': 'ویرایش اطلاعات با موفقیت انجام شد.'

}
"""


class EditPro(CustomUser):
    old_password = models.CharField(max_length = 50)


class EditProSerializer(serializers.ModelSerializer):
    class Meta:
        model = EditPro
        fields = (
            'username', 'email', 'old_password', 'password', 'birth_date', 'gender', 'location', 'city', 'first_name',
            'last_name'
        )


salesman_signup_first = """
{
    'email': 'ghazal04194@gmail.com',
    'password': 'This_is/A strong ##PASSword!'
}
"""

email_added_successfully = """
{
    'result': true,
    'message': 'اطلاعات با موفقیت ذخیره شد.'
}
"""


class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('email', 'password')


salesman_signup_second = """
{
    'email': 'ghazal04194@gmail.com',
    'code': '1111'
}
"""

salesman_signup_successful = """
{
    "result": true,
    "message": "ثبت نام با موفقیت انجام شد."
}
"""


class SalesmanCode4DigitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Code4DigitSalesman
        exclude = ('password',)


salesman_signup_final = """
{
    'phone_number': '09131674340',
    'username': 'ghazal04194',
    'password': 'This_is/A strong ##PASSword!',
    'first_name': 'Ghazal',
    'last_name': 'Rabiei',
    'birth_date': '1998-09-19',
    'email': 'ghazal04194@gmail.com',
    'gender': 'f',
    'location': '30.674507,21.690543',
    'city': '2',
    'avatar': 'Picture's Path'
}
"""

salesman_signup_successful2 = """
{
    'result': True,
    'message': 'ثبت نام با موفقیت انجام شد.',
    'token': 'e52965d673398d2f27af363b6836fc7db2d73237'
}
"""


class SalesmanInfo(CustomUser):
    avatar = models.ImageField()


class SalesmanInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesmanInfo
        fields = (
            'username', 'email', 'password', 'birth_date', 'gender', 'location', 'phone_number', 'city', 'first_name',
            'last_name', 'avatar'
        )


salesman_email = """
{
    'email': 'ghazal04194@gmai.com'
}
"""


class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('email',)


salesman_login = """
{
    'email': 'ghazal04194@gmail.com',
    'password': 'This_is/A strong ##PASSword!'
}
"""

salesman_login_successful = """
{
    "result": true,
    "message": "ورود با موفقیت انجام شد.",
    "salesman": {
        "id": 1,
        "avatar": "/new-temp/Salesman/ghazal04194.jpg",
        "first_name": "Ghazal",
        "last_name": "Rabiei"
    },
    "token": "e52965d673398d2f27af363b6836fc7db2d73237"
}
"""


class SalesmanLoginInfo(models.Model):
    first_name = models.CharField(max_length = 30, blank = True)
    last_name = models.CharField(max_length = 150, blank = True)
    avatar = models.ImageField()


class ResponseWithTokenWithSalesman(ResponseWithToken):
    salesman = models.OneToOneField(SalesmanLoginInfo, on_delete = models.CASCADE, related_name = 'response')


class LoginSalesmanSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResponseWithTokenWithSalesman
        fields = '__all__'
        depth = 1


salesman_profile_edit_pro = """
{
    'avatar': 'New Picture's Path',
    'birth_data': '1997-01-02',
    'email': 
}
"""

salesman_edit_pro_successful = """
{
    "result": True,
    "message": "ویرایش اطلاعات با موفقیت انجام شد."
}
"""

# class EditSalesman
