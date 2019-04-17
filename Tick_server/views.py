from django.contrib.auth import login
from rest_framework.response import Response
from rest_framework.views import APIView

from Tick_server.models import Code4Digit, Customer, Discount
from Tick_server.serializers import CustomerSerializer, DiscountSerializer


# noinspection PyMethodMayBeStatic
class SignUpFirst(APIView):
    def post(self, request, format = None):
        phone = request.data['phone_number']
        # serializer = CustomerSerializer(data = request.data)
        if Customer.objects.filter(phone_number = phone).count() == 1:
            return Response({
                'result': False,
                'message': 'کاربری با این شماره تلفن قبلاً ثبت‌نام کرده.',
            })
        else:
            Code4Digit.objects.create(phone_number = phone, code = '1111')
            return Response({
                'result': True,
                'message': 'شماره تلفن با موفقیت ثبت شد.',
            })


# noinspection PyMethodMayBeStatic
class SignUpSecond(APIView):
    def post(self, request, format = None):
        phone = request.data['phone_number']
        code = request.data['code']
        if Code4Digit.objects.filter(phone_number = phone, code = code).count() == 1:
            return Response({
                'result': True,
                'message': 'ثبت‌نام با موفقیت انجام شد.',
            })
        else:
            return Response({
                'result': False,
                'message': 'کد وارد شده صحیح نیست. لطفاً دوباره امتحان کنید.',
            })


class ResendCode(APIView):
    def post(self, request, format = None):
        phone = request.data['phone_number']
        Code4Digit.objects.get(phone_number = phone).update(code = '1111')
        return Response({
            'result': True,
            'message': 'کد مجدداً ارسال شد.',
        })


class SignUpFinal(APIView):
    def post(self, request, format = None):
        serializer = CustomerSerializer(data = request.data)
        if not serializer.is_valid():
            print(serializer.errors)
            return Response({
                'result': False,
                'message': 'ثبت‌نام با خطا مواجه شد.',
            })
        else:
            serializer.save()
            Code4Digit.objects.get(phone_number = request.data['phone_number']).delete()
            return Response({
                'result': True,
                'message': 'ثبت‌نام با موفقیت انجام شد.',
            })


class Login(APIView):
    def post(self, request, format = None):
        phone = request.data['phone_number']
        password = request.data['password']
        customer = Customer.objects.filter(phone_number = phone)
        if customer.count() == 0:
            return Response({
                'result': False,
                'message': 'کاربری با این شماره یافت نشد.',
            })
        if not customer.first().check_password(password):
            return Response({
                'result': False,
                'message': 'رمز عبور اشتباه است.',
            })
        login(request, customer.first())
        serializer = CustomerSerializer(customer[0])
        json = serializer.data
        return Response({
            'result': True,
            'message': 'ورود با موفقیت انجام شد.',
            'customer': json
        })


class ActiveDiscountListView(APIView):
    def post(self, request, Format = None):
        page = request.data['page']
        offset = request.data['offset']
        phone = request.data['phone_number']
        discounts = Discount.objects.filter(active = True, customer = Customer.objects.get(phone_number = phone))[
                    page - 1 * offset: page * offset]
        serializer = DiscountSerializer(discounts, many = True)
        return Response({
            'result': True,
            'message': 'جستجو با موفقیت انجام شد.',
            'discounts': serializer.data
        })


class InactiveDiscountListView(APIView):
    def post(self, request, Format = None):
        page = request.data['page']
        offset = request.data['offset']
        phone = request.data['phone_number']
        discounts = Discount.objects.filter(active = False, customer = Customer.objects.get(phone_number = phone))[
                    page - 1 * offset: page * offset]
        serializer = DiscountSerializer(discounts, many = True)
        return Response({
            'result': True,
            'message': 'جستجو با موفقیت انجام شد.',
            'discounts': serializer.data
        })
