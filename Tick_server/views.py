from django.contrib.auth import login
from rest_framework.response import Response
from rest_framework.views import APIView

from Tick_server.models import Code4Digit, Customer, Discount, Code4DigitSalesman, Salesman
from Tick_server.serializers import CustomerSerializer, DiscountSerializer, PollSerializer, UserSerializer, \
    SalesmanSerializer


# noinspection PyMethodMayBeStatic
class SignUpFirst(APIView):
    def post(self, request, format = None):
        phone = request.data['phone_number']
        # serializer = CustomerSerializer(data = request.data)
        if Customer.objects.filter(user__phone_number = phone).count() == 1:
            return Response({
                'result': False,
                'message': 'کاربری با این شماره تلفن قبلاً ثبت‌نام کرده.',
            })
        else:
            Code4Digit.objects.update_or_create(phone_number = phone, defaults = {'code': '1111'})
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
        Code4Digit.objects.filter(phone_number = phone).update(code = '1111')
        return Response({
            'result': True,
            'message': 'کد مجدداً ارسال شد.',
        })


class SignUpFinal(APIView):
    def post(self, request, format = None):
        copy = request.data.copy()
        copy.update({'user_type': 'CU'})
        serializer = UserSerializer(data = copy)
        if not serializer.is_valid():
            print(serializer.errors)
            return Response({
                'result': False,
                'message': 'ثبت‌نام با خطا مواجه شد.',
            })
        else:
            user = serializer.save()
            Customer.objects.create(user = user)
            Code4Digit.objects.get(phone_number = copy['phone_number']).delete()
            return Response({
                'result': True,
                'message': 'ثبت‌نام با موفقیت انجام شد.',
            })


class Login(APIView):
    def post(self, request, format = None):
        phone = request.data['phone_number']
        password = request.data['password']
        customer = Customer.objects.filter(user__phone_number = phone)
        if customer.count() == 0:
            return Response({
                'result': False,
                'message': 'کاربری با این شماره یافت نشد.',
            })
        if not customer[0].check_password(password):
            return Response({
                'result': False,
                'message': 'رمز عبور اشتباه است.',
            })
        login(request, customer[0].user)
        serializer = CustomerSerializer(customer[0])
        return Response({
            'result': True,
            'message': 'ورود با موفقیت انجام شد.',
            'customer': serializer.data
        })


class SignUpFirstSalesman(APIView):
    def post(self, request, format = None):
        email = request.data['email']
        password = request.data['password']
        if Customer.objects.filter(user__email = email).count() == 1:
            return Response({
                'result': False,
                'message': 'کاربری با این ایمیل قبلاً ثبت‌نام کرده.',
            })
        else:
            Code4DigitSalesman.objects.update_or_create(email = email, password = password, defaults = {'code': '1111'})
            return Response({
                'result': True,
                'message': 'اطلاعات با موفقیت ذخیره شد.',
            })


class SignUpSecondSalesman(APIView):
    def post(self, request, format = None):
        email = request.data['email']
        code = request.data['code']
        if Code4DigitSalesman.objects.filter(email = email, code = code).count() == 1:
            return Response({
                'result': True,
                'message': 'ثبت‌نام با موفقیت انجام شد.',
            })
        else:
            return Response({
                'result': False,
                'message': 'کد وارد شده صحیح نیست. لطفاً دوباره امتحان کنید.',
            })


class SignUpFinalSalesman(APIView):
    def post(self, request, format = None):
        copy = request.data.copy()
        copy.update({'user_type': 'SM'})
        print(copy)
        serializer = UserSerializer(data = copy)
        if not serializer.is_valid():
            print(serializer.errors)
            return Response({
                'result': False,
                'message': 'ثبت‌نام با خطا مواجه شد.',
            })
        else:
            user = serializer.save()
            Salesman.objects.create(user = user)
            Code4DigitSalesman.objects.get(email = copy['email']).delete()
            return Response({
                'result': True,
                'message': 'ثبت‌نام با موفقیت انجام شد.',
            })


class ResendCodeSalesman(APIView):
    def post(self, request, format = None):
        email = request.data['email']
        Code4DigitSalesman.objects.filter(email = email).update(code = '1111')
        return Response({
            'result': True,
            'message': 'کد مجدداً ارسال شد.',
        })


class LoginSalesman(APIView):
    def post(self, request, format = None):
        email_field = False
        try:
            email = request.data['email']
            email_field = True
        except KeyError:
            username = request.data['username']

        password = request.data['password']
        if email_field:
            salesman = Salesman.objects.filter(user__email = email)
        else:
            salesman = Salesman.objects.filter(user__username = username)

        if salesman.count() == 0:
            return Response({
                'result': False,
                'message': 'کاربری با این شماره یافت نشد.',
            })
        if not salesman[0].check_password(password):
            return Response({
                'result': False,
                'message': 'رمز عبور اشتباه است.',
            })
        login(request, salesman[0].user)
        serializer = SalesmanSerializer(salesman[0])
        return Response({
            'result': True,
            'message': 'ورود با موفقیت انجام شد.',
            'salesman': serializer.data
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


class NotCompletedPollList(APIView):
    def post(self, request, Format = None):
        page = request.data['post']
        offset = request.data['offset']
        phone = request.data['phone_number']
        customer = Customer.objects.get(phone_number = phone)
        polls = []
        polls.extend(customer.linear_scale_poll_answer.filter(completed = False))
        polls.extend(customer.paragraph_poll_answers.filter(completed = False))
        polls.extend(customer.short_answer_poll_answers.filter(completed = False))
        polls.extend(customer.multiple_choice_poll_answers.filter(completed = False))
        polls.extend(customer.checkbox_poll_answers.filter(completed = False))
        polls.sort(key = lambda poll: poll.remaining_time)
        polls = polls[page - 1 * offset: page * offset]
        serializer = PollSerializer(polls, many = True)
        return Response({
            'result': True,
            'message': 'جستجو با موفقیت انجام شد.',
            'polls': serializer.data
        })


class CompletePoll(APIView):
    def post(self, request, Format = None):
        poll_id = request.data['poll_id']
        username = request.data['username']
        poll_type = request.data['poll_type']
