import string
from typing import Union

from django.contrib.auth import login
from django.contrib.auth.views import LogoutView
from django.core.files import File
from django.db import transaction
from django.http import FileResponse
from django.utils import timezone
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from Tick_server.models import *
from Tick_server.responses import *
from Tick_server.serializers import *


# noinspection PyMethodMayBeStatic
class SignUpFirstCustomer(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request) -> Response:
        """
        Gets and saves new customers I{phone_number}
        @param request: includes I{phone_number} only
        @return: Response showing whether saving phone number was successful or not.
        """
        if not request.user.is_superuser:
            return Response(access_denied)
        phone = request.data['phone_number']
        if Customer.objects.filter(user__phone_number = phone).count() == 1:
            return Response(customer_already_exists)
        else:
            Code4Digit.objects.update_or_create(phone_number = phone, defaults = {'code': '1111'})
            return Response(phone_added_successfully)


# noinspection PyMethodMayBeStatic
class SignUpSecondCustomer(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request) -> Response:
        """
        Gets phone number and code sent to user and checks if it's valid
        @param request: includes phone number and code
        @return: Response showing whether the code is valid and sign up is successful or not
        """
        if not request.user.is_superuser:
            return Response(access_denied)
        phone = request.data['phone_number']
        code = request.data['code']
        if Code4Digit.objects.filter(phone_number = phone, code = code).count() == 1:
            return Response(customer_signup_successful)
        else:
            return Response(customer_code_incorrect)


# noinspection PyMethodMayBeStatic
class ResendCodeCustomer(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request) -> Response:
        """
        Gets phone number and sends a new code to that number
        @param request: includes phone number only
        @return: Response always contains true
        """
        if not request.user.is_superuser:
            return Response(access_denied)
        phone = request.data['phone_number']
        codes = Code4Digit.objects.filter(phone_number = phone)
        if codes.count() == 0:
            return Response(customer_code_resend_failed)
        codes.update(code = '1111')
        return Response(customer_code_resent)


# noinspection PyMethodMayBeStatic
class SignUpFinalCustomer(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request) -> Response:
        """
        Gets phone number and other information to sign up a user.
        @param request: includes phone number and all necessary information to create new user
        @return: Response showing whether sign up is successful or not
        """
        if not request.user.is_superuser:
            return Response(access_denied)
        copy = request.data.copy()
        copy.update({'user_type': 'CU'})
        serializer = UserSerializer(data = copy)
        code = Code4Digit.objects.filter(phone_number = copy['phone_number'])
        if not serializer.is_valid():
            print(serializer.errors)
            return Response(customer_signup_failed)
        if code.count() == 0:
            print('invalid phone_number specified')
            return Response(customer_signup_failed)
        else:
            user = serializer.save()
            Customer.objects.create(user = user)
            token, _ = Token.objects.get_or_create(user = user)
            code[0].delete()
            response = customer_signup_successful.copy()
            response.update({'token': token.key})
            return Response(response)


# noinspection PyMethodMayBeStatic
class LoginCustomer(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request) -> Response:
        """
        Gets phone number and login credentials of a user and tries to login that user
        @param request: containing phone number and password
        @return: Response showing whether login is successful or not, if login is successful then sends all user
        information
        """
        if not request.user.is_superuser:
            return Response(access_denied)
        phone = request.data['phone_number']
        password = request.data['password']
        customer = Customer.objects.filter(user__phone_number = phone)
        if customer.count() == 0:
            return Response(customer_not_found)
        if not customer[0].check_password(password):
            return Response(customer_wrong_password)
        login(request, customer[0].user)
        serializer = UserSerializer(customer[0].user)
        token, _ = Token.objects.get_or_create(user = customer[0].user)
        result = customer_login_successful.copy()
        result.update({'customer_info': serializer.data})
        result.update({'token': token.key})
        return Response(result)


# noinspection PyMethodMayBeStatic
class EditCustomerProfile(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request) -> Response:
        """
        Authenticates the user, validates and changes the information he sends via I{request}.
        @param request: Containing information wanted to edit.
        @return: I{Response} showing whether information updated or not.
        """
        customer = Customer.objects.filter(user__phone_number = request.data['phone_number'],
                                           user__username = request.user)
        _mutable = request.data._mutable
        request.data._mutable = True
        if customer.count() == 0:
            return Response(access_denied)
        customer = customer[0]
        if 'old_password' in request.data:
            old_password = request.data.pop('old_password')
            if not customer.check_password(old_password[0]):
                return Response({
                    'result': False,
                    'message': 'رمز قبلی نادرست وارد شده است.'
                })
        serializer = UserSerializer(customer.user, data = request.data, partial = True)
        if not serializer.is_valid():
            print(serializer.errors)
            return Response({
                'result': False,
                'message': 'ویرایش اطلاعات با خطا مواجه شد.'
            })
        else:
            serializer.save()
            return Response({
                'result': True,
                'message': 'ویرایش اطلاعات با موفقیت انجام شد.',
            })


# noinspection PyMethodMayBeStatic
class SignUpFirstSalesman(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request) -> Response:
        """
        Gets and saves new salesman email and password
        @param request: includes email and password
        @return: Response showing whether saving email and password was successful or not.
        """
        email = request.data['email']
        password = request.data['password']
        if Salesman.objects.filter(user__email = email).count() == 1:
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


# noinspection PyMethodMayBeStatic
class SignUpSecondSalesman(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request) -> Response:
        """
        Gets email and code sent to user and checks if it's valid
        @param request: includes email and code
        @return: Response showing whether the code is valid and sign up is successful or not
        """
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


# noinspection PyMethodMayBeStatic
class SignUpFinalSalesman(APIView):
    permission_classes = []
    authentication_classes = []

    @transaction.atomic
    def post(self, request) -> Response:
        """
        Gets email and other information to sign up a user.
        @param request: includes email and all necessary information to create new user
        @return: Response showing whether sign up is successful or not
        """
        request.data._mutable = True
        request.data.update({'user_type': 'SM'})
        try:
            with transaction.atomic():
                serializer = UserSerializer(data = request.data)
                serializer.is_valid(raise_exception = True)
                user = serializer.save()
                request.data.update({'user': user.pk})
                serializer = SalesmanSerializer(data = request.data)
                serializer.is_valid(raise_exception = True)
                serializer.save()
                Code4DigitSalesman.objects.get(email = request.data['email']).delete()
                return Response({
                    'result': True,
                    'message': 'ثبت‌نام با موفقیت انجام شد.',
                })
        except serializers.ValidationError as e:
            print(e)
            return Response({
                'result': False,
                'message': 'ثبت‌نام با خطا مواجه شد.'
            })


# noinspection PyMethodMayBeStatic
class ResendCodeSalesman(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request) -> Response:
        """
        Gets email and sends a new code to that email
        @param request: includes email only
        @return: Response always contains true
        """
        email = request.data['email']
        Code4DigitSalesman.objects.filter(email = email).update(code = '1111')
        return Response({
            'result': True,
            'message': 'کد مجدداً ارسال شد.',
        })


# noinspection PyMethodMayBeStatic
class LoginSalesman(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request) -> Response:
        """
        Gets email or username and login credentials of a user and tries to login that user
        @param request: containing email or username and password
        @return: Response showing whether login is successful or not, if login is successful then sends all user
        information
        """
        email = request.data['email']
        password = request.data['password']
        salesman = Salesman.objects.filter(user__email = email)
        if salesman.count() == 0:
            return Response({
                'result': False,
                'message': 'کاربری با این ایمیل یافت نشد.',
            })
        if not salesman[0].check_password(password):
            return Response({
                'result': False,
                'message': 'رمز عبور اشتباه است.',
            })
        login(request, salesman[0].user)
        serializer = SalesmanSerializer(salesman[0])
        request.data._mutable = True
        copy = serializer.data.copy()
        id_user = copy.pop('user')
        user = CustomUser.objects.get(id = id_user)
        print(copy)
        shops = salesman[0].shops.all()
        shops_list = []
        for shop in shops:
            shops_list.append({'id': shop.id, 'name': shop.name})
        copy.update({'first_name': user.first_name, 'last_name': user.last_name, 'shops': shops_list})
        return Response({
            'result': True,
            'message': 'ورود با موفقیت انجام شد.',
            'salesman': copy
        })


# noinspection PyMethodMayBeStatic
class AddShop(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)

    def post(self, request) -> Response:
        """
        Adds a new shop.
        @param request: containing name, address and all other information to add a new shop
        @return: Response showing whether adding a new shop was successful, if adding is successful, then sends shop
        id
        """
        salesman = Salesman.objects.get(pk = request.data['salesman']).user
        if salesman != request.user:
            return Response({
                'result': False,
                'message': 'دسترسی رد شد.'
            })
        serializer = ShopSerializer(data = request.data)
        if not serializer.is_valid():
            print(serializer.errors)
            return Response({
                'result': False,
                'message': 'اضافه کردن فروشگاه با خطا مواجه شد.'
            })
        else:
            shop = serializer.save()
            return Response({
                'result': True,
                'message': 'اضافه کردن فروشگاه با موفقیت انجام شد.',
                'shop_id': shop.id
            })


# noinspection PyMethodMayBeStatic
class AddDiscount(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)

    def post(self, request) -> Response:
        """
        Adds discount by number of count.
        @param request: containing discount information and count of discount to add
        @return: Response showing whether adding discount is successful or not
        """
        shop = Shop.objects.get(pk = request.data['shop'])
        shops = request.user.salesman.shops
        if shops.filter(pk = shop.pk).count() == 0:
            return Response({
                'result': False,
                'message': 'دسترسی رد شد.'
            })
        copy = request.data.copy()
        days = int(copy.pop('days')[0])
        count = int(copy.pop('count')[0])
        percent = int(copy.pop('percent')[0])
        copy.update({'count': count})
        copy.update({'percent': percent})
        copy.update({'days': days})
        serializer = CandidateProductSerializer(data = copy)
        if not serializer.is_valid():
            print(serializer.errors)
            return Response({
                'result': False,
                'message': 'اضافه کردن تخفیف با خطا مواجه شد.'
            })
        else:
            serializer.save()
            return Response({
                'result': True,
                'message': 'اضافه کردن تخفیف با موفقیت انجام شد.'
            })


# noinspection PyMethodMayBeStatic
class ActiveDiscountListView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request) -> Response:
        """
        Gets phone number, page and offset and retrieve active discounts list of that customer
        @param request: Containing phone number, page and offset
        @return: Response containing active discounts belong to that customer
        """
        page = int(request.data['page'])
        offset = int(request.data['offset'])
        phone = request.data['phone_number']
        user = CustomUser.objects.filter(phone_number = phone, username = request.user)
        if user.count() == 0:
            return Response({
                'result': False,
                'message': 'دسترسی رد شد.'
            })
        user = user[0]
        discounts = Discount.objects.filter(active = True, customer = Customer.objects.get(user = user))[
                    page * offset: page * offset + offset]
        serializer = DiscountSerializer(discounts, many = True)
        return Response({
            'result': True,
            'message': 'جستجو با موفقیت انجام شد.',
            'discounts': serializer.data
        })


# noinspection PyMethodMayBeStatic
class InactiveDiscountListView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request) -> Response:
        """
        Gets phone number, page and offset and retrieve inactive discounts list of that customer
        @param request: Containing phone number, page and offset
        @return: Response containing inactive discounts belong to that customer
        """
        page = int(request.data['page'])
        offset = int(request.data['offset'])
        phone = request.data['phone_number']
        user = CustomUser.objects.filter(phone_number = phone, username = request.user)
        if user.count() == 0:
            return Response({
                'result': False,
                'message': 'دسترسی رد شد.'
            })
        user = user[0]
        discounts = Discount.objects.filter(active = False, customer = Customer.objects.get(user = user))[
                    page * offset: page * offset + offset]
        serializer = DiscountSerializer(discounts, many = True)
        return Response({
            'result': True,
            'message': 'جستجو با موفقیت انجام شد.',
            'discounts': serializer.data
        })


# noinspection PyMethodMayBeStatic, PyUnusedLocal
class GetCities(APIView):
    permission_classes = []
    authentication_classes = []

    def get(self, request) -> Response:
        """
        Returns all cities.
        @type request: Unused
        @return: Response containing all cities in the database.
        """
        cities = City.objects.all()
        data = []
        for city in cities:
            data.append({'id': city.pk, 'name': city.name})
        return Response({
            'result': True,
            'message': 'نام شهرها',
            'cities': data
        })


# noinspection PyMethodMayBeStatic, PyUnusedLocal
class GetShopKinds(APIView):
    permission_classes = []
    authentication_classes = []

    def get(self, request) -> Response:
        """
        Returns ShopKind corresponding requested I{id}.
        @param request: Unused
        @return: Response showing whether ShopKind was found or not. If ShopKind was found, it will be returned
        respectively.
        """
        data = []
        shop_kinds = ShopKind.objects.all()
        for kind in shop_kinds:
            data.append({'id': kind.pk, 'name': kind.name})
        return Response({
            'result': True,
            'message': 'نوع فروشگاه ها',
            'shop_kinds': data
        })


# noinspection PyMethodMayBeStatic
class EditSalesmanProfileView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)

    @transaction.atomic
    def post(self, request) -> Response:
        """
        Authenticates the user, validates and changes the information he sends via I{request}.
        @param request: Containing information wanted to edit.
        @return: I{Response} showing whether information updated or not.
        """
        salesman = Salesman.objects.get(user__email = request.data['email'])
        if 'old_password' in request.data:
            old_password = request.data.pop('old_password')
            if not salesman.check_password(old_password[0]):
                return Response({
                    'result': False,
                    'message': 'رمز وارد شده صحیح نیست.'
                })
        try:
            with transaction.atomic():
                serializer = UserSerializer(salesman.user, request.data, partial = True)
                serializer.is_valid(raise_exception = True)
                serializer.save()
                if 'avatar' in request.data:
                    serializer = SalesmanSerializer(salesman, request.data, partial = True)
                    serializer.is_valid(raise_exception = True)
                    serializer.save()
                return Response({
                    'result': True,
                    'message': 'ویرایش اطلاعات با موفقیت انجام شد.'
                })
        except serializers.ValidationError as e:
            print(e)
            return Response({
                'result': False,
                'message': 'ویرایش اطلاعات با خطا مواجه شد.'
            })


# noinspection PyMethodMayBeStatic
class GetSalesmanAvatar(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)

    def get(self, request) -> FileResponse:
        """
        Gets the I{avatar} of salesman.
        @param request: containing authenticated user object.
        @return: FileResponse containing salesman's I{avatar}
        """
        file = File(open('new-temp/' + str(request.user.salesman.avatar), 'rb'))
        return FileResponse(file)


# noinspection PyMethodMayBeStatic
class GetShopPicture(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)

    def post(self, request) -> Union[Response, FileResponse]:
        """
        Gets the I{picture} of shop.
        @param request: containing shop's I{pk}.
        @return: FileResponse containing shop's I{picture} or Response if access is denied.
        """
        shop = Shop.objects.get(pk = request.data['shop'])
        shops = request.user.salesman.shops
        if shops.filter(pk = shop.pk).count() == 0:
            return Response({
                'result': False,
                'message': 'دسترسی رد شد.'
            })
        file = File(open('new-temp/' + str(shop.picture)), 'rb')
        return FileResponse(file)


# noinspection PyMethodMayBeStatic
class GetShopBusinessLicense(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)

    def post(self, request) -> Union[Response, FileResponse]:
        """
        Gets the I{business_license} of shop.
        @param request: containing shop's I{pk}.
        @return: FileResponse containing shop's I{business_license} or Response if access is denied.
        """
        shop = Shop.objects.get(pk = request.data['shop'])
        shops = request.user.salesman.shops
        if shops.filter(pk = shop.pk).count() == 0:
            return Response({
                'result': False,
                'message': 'دسترسی رد شد.'
            })
        file = File(open('new-temp/' + str(shop.business_license)), 'rb')
        return FileResponse(file)


# # TODO
# class NotCompletedPollList(APIView):
#     def post(self, request, Format = None):
#         page = request.data['post']
#         offset = request.data['offset']
#         phone = request.data['phone_number']
#         customer = Customer.objects.get(phone_number = phone)
#         polls = []
#         polls.extend(customer.linear_scale_poll_answer.filter(completed = False))
#         polls.extend(customer.paragraph_poll_answers.filter(completed = False))
#         polls.extend(customer.short_answer_poll_answers.filter(completed = False))
#         polls.extend(customer.multiple_choice_poll_answers.filter(completed = False))
#         polls.extend(customer.check_box_poll_answers.filter(completed = False))
#         polls.sort(key = lambda poll: poll.remaining_time)
#         polls = polls[page - 1 * offset: page * offset]
#         serializer = PollSerializer(polls, many = True)
#         return Response({
#             'result': True,
#             'message': 'جستجو با موفقیت انجام شد.',
#             'polls': serializer.data
#         })


# noinspection PyMethodMayBeStatic
class AddPoll(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)

    @transaction.atomic
    def post(self, request) -> Response:
        """
        Adds poll.
        @param request: Containing data needed to add poll.
        @return: Response showing whether adding was successful or not.
        """
        shop = Shop.objects.get(pk = request.data['shop'])
        shops = request.user.salesman.shops
        if shops.filter(pk = shop.pk).count() == 0:
            return Response({
                'result': False,
                'message': 'دسترسی رد شد.'
            })
        request.data._mutable = True
        type_poll = request.data['type_poll']
        if type_poll == 'CheckBoxPoll':
            try:
                with transaction.atomic():
                    answer_texts = request.data.pop('answer_texts')
                    answer_texts = (answer_texts[0]).split(',')
                    poll_serializer = PollSerializer(data = request.data)
                    poll_serializer.is_valid(raise_exception = True)
                    poll = poll_serializer.save()
                    data = {
                        'poll': poll.pk
                    }
                    checkbox_serializer = CheckBoxPollSerializer(data = data)
                    checkbox_serializer.is_valid(raise_exception = True)
                    checkbox_poll = checkbox_serializer.save()
                    index = 0
                    temp = []
                    for ans in answer_texts:
                        data = {
                            'index': index,
                            'answer_text': ans,
                            'poll': checkbox_poll.pk
                        }
                        option_serializer = CheckBoxPollOptionSerializer(data = data)
                        temp.append(option_serializer)
                        option_serializer.is_valid(raise_exception = True)
                        index += 1
                    for ans in temp:
                        ans.save()
                    return Response({
                        'result': True,
                        'message': 'اضافه کردن نظرسنجی با موفقیت انجام شد.'
                    })
            except serializers.ValidationError as e:
                print(e)
                return Response({
                    'result': False,
                    'message': 'اضافه کردن نظرسنجی با خطا مواجه شد.'
                })
        elif type_poll == 'MultipleChoicePoll':
            try:
                with transaction.atomic():
                    answer_texts = request.data.pop('answer_texts')
                    answer_texts = (answer_texts[0]).split(',')
                    poll_serializer = PollSerializer(data = request.data)
                    poll_serializer.is_valid(raise_exception = True)
                    poll = poll_serializer.save()
                    data = {
                        'poll': poll.pk
                    }
                    multiple_serializer = MultipleChoicePollSerializer(data = data)
                    multiple_serializer.is_valid(raise_exception = True)
                    multiple_poll = multiple_serializer.save()
                    temp = []
                    index = 0
                    for ans in answer_texts:
                        data = {
                            'index': index,
                            'answer_text': ans,
                            'poll': multiple_poll.pk
                        }
                        option_serializer = MultipleChoiceOptionSerializer(data = data)
                        temp.append(option_serializer)
                        option_serializer.is_valid(raise_exception = True)
                        index += 1
                    for ans in temp:
                        ans.save()
                    return Response({
                        'result': True,
                        'message': 'اضافه کردن نظرسنجی با موفقیت انجام شد.'
                    })
            except serializers.ValidationError as e:
                print(e)
                return Response({
                    'result': False,
                    'message': 'اضافه کردن نظرسنجی با خطا مواجه شد.'
                })
        elif type_poll == 'ParagraphPoll':
            try:
                with transaction.atomic():
                    poll_serializer = PollSerializer(data = request.data)
                    poll_serializer.is_valid(raise_exception = True)
                    poll = poll_serializer.save()
                    data = {
                        'poll': poll.pk
                    }
                    paragraph_serializer = ParagraphPollSerializer(data = data)
                    paragraph_serializer.is_valid(raise_exception = True)
                    return Response({
                        'result': True,
                        'message': 'اضافه کردن نظرسنجی با موفقیت انجام شد.'
                    })
            except serializers.ValidationError as e:
                print(e)
                return Response({
                    'result': False,
                    'message': 'اضافه کردن نظرسنجی با خطا مواجه شد.'
                })
        elif type_poll == 'LinearScalePoll':
            try:
                with transaction.atomic():
                    poll_serializer = PollSerializer(data = request.data)
                    poll_serializer.is_valid(raise_exception = True)
                    poll = poll_serializer.save()
                    request.data._mutable = True
                    request.data.update({'poll': poll.pk})
                    linear_serializer = LinearScalePollSerializer(data = request.data)
                    linear_serializer.is_valid(raise_exception = True)
                    linear_serializer.save()
                    return Response({
                        'result': True,
                        'message': 'اضافه کردن نظرسنجی با موفقیت انجام شد.'
                    })
            except serializers.ValidationError as e:
                print(e)
                return Response({
                    'result': False,
                    'message': 'اضافه کردن نظرسنجی با خطا مواجه شد.'
                })
        else:
            try:
                with transaction.atomic():
                    poll_serializer = PollSerializer(data = request.data)
                    poll_serializer.is_valid(raise_exception = True)
                    poll_serializer.save()
                    short_answer_serializer = ShortAnswerSerializer(data = request.data)
                    short_answer_serializer.is_valid(raise_exception = True)
                    return Response({
                        'result': True,
                        'message': 'اضافه کردن نظرسنجی با موفقیت انجام شد.'
                    })
            except serializers.ValidationError as e:
                print(e)
                return Response({
                    'result': False,
                    'message': 'اضافه کردن نظرسنجی با خطا مواجه شد.'
                })


# noinspection DjangoOrm, PyMethodMayBeStatic
class SubmitPoll(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request) -> Response:
        """
        Submits a poll and gives a discount to customer.
        @param request: Containing I{poll_id} and the answer to poll.
        @return: Response having discount, if any exists.
        """
        customer = Customer.objects.filter(user__phone_number = request.data['phone_number'], user = request.user)
        if customer.count() == 0:
            return Response({
                'result': False,
                'message': 'دسترسی رد شد.'
            })
        customer = customer[0]
        poll = Poll.objects.get(id = request.data['poll_id'])
        if 'linear_scale_answer' in request.data:
            linear_poll = poll.linear_scale_poll
            linear_scale_poll_ans = LinearScalePollAnswer.objects.get(poll = linear_poll, customer = customer,
                                                                      poll_answer__completed = False)
            linear_scale_poll_ans.answer = int(request.data['linear_scale_answer'])
            linear_scale_poll_ans.poll_answer.completed = True
            linear_scale_poll_ans.poll_answer.save()
            linear_scale_poll_ans.save()
        elif 'short_answer_text' in request.data:
            short_poll = poll.short_answer_poll
            short_answer_poll_ans = ShortAnswerPollAnswer.objects.get(poll = short_poll, customer = customer,
                                                                      poll_answer__completed = False)
            short_answer_poll_ans.answer_text = request.data['short_answer_text']
            short_answer_poll_ans.poll_answer.completed = True
            short_answer_poll_ans.poll_answer.save()
            short_answer_poll_ans.save()
        elif 'paragraph_text' in request.data:
            paragraph_poll = poll.paragraph_poll
            paragraph_poll_ans = ParagraphPollAnswer.objects.get(poll = paragraph_poll, customer = customer,
                                                                 poll_answer__completed = False)
            paragraph_poll_ans.answer_text = request.data['paragraph_text']
            paragraph_poll_ans.poll_answer.completed = True
            paragraph_poll_ans.poll_answer.save()
            paragraph_poll_ans.save()
        elif 'check_box_answer' in request.data:
            check_box_poll = poll.check_box_poll
            check_box_poll_ans = CheckBoxPollAnswer.objects.get(check_box_poll = check_box_poll, customer = customer,
                                                                poll_answer__completed = False)
            answers = request.data['check_box_answer'][1:-1].split(',')
            for ans in answers:
                check_box_poll_ans.options.add(check_box_poll.options.get(index = int(ans)))
            check_box_poll_ans.poll_answer.completed = True
            check_box_poll_ans.poll_answer.save()
            check_box_poll_ans.save()
        else:
            multiple_choice_poll = poll.multiple_choice_poll
            multiple_choice_poll_ans = MultipleChoiceAnswer.objects.get(multiple_choice = multiple_choice_poll,
                                                                        customer = customer,
                                                                        poll_answer__completed = False)
            index = int(request.data['multiple_choice_answer'])
            multiple_choice_poll_ans.option = multiple_choice_poll.options.get(index = index)
            multiple_choice_poll_ans.poll_answer.completed = True
            multiple_choice_poll_ans.poll_answer.save()
            multiple_choice_poll_ans.save()
        shop = Shop.objects.get(id = poll.shop.id)
        my_polls = Poll.objects.filter(Q(paragraph_poll__paragraph_poll_answers__customer = customer,
                                         paragraph_poll__paragraph_poll_answers__poll_answer__completed = True) |
                                       Q(short_answer_poll__short_answer_poll_answers__customer = customer,
                                         short_answer_poll__short_answer_poll_answers__poll_answer__completed = True) |
                                       Q(linear_scale_poll__linear_scale_poll_answers__customer = customer,
                                         linear_scale_poll__linear_scale_poll_answers__poll_answer__completed = True) |
                                       Q(check_box_poll__check_box_poll_answers__customer = customer,
                                         check_box_poll__check_box_poll_answers__poll_answer__completed = True) |
                                       Q(multiple_choice_poll__multiple_choice_answers__customer = customer,
                                         multiple_choice_poll__multiple_choice_answers__poll_answer__completed = True))
        poll_count = my_polls.filter(shop = shop).count()
        discounts = CandidateProduct.objects.filter(expire_date__gte = timezone.now(), shop = shop, count__gt = 0)
        my_discounts = None
        if 50 <= poll_count:
            my_discounts = discounts.filter(percent__lte = 100, percent__gt = 90)
        if 45 <= poll_count < 50 or (my_discounts and my_discounts.count() == 0):
            my_discounts = discounts.filter(percent__lte = 90, percent__gt = 80)
        if 40 <= poll_count < 45 or (my_discounts and my_discounts.count() == 0):
            my_discounts = discounts.filter(percent__lte = 80, percent__gt = 70)
        if 35 <= poll_count < 40 or (my_discounts and my_discounts.count() == 0):
            my_discounts = discounts.filter(percent__lte = 70, percent__gt = 60)
        if 30 <= poll_count < 35 or (my_discounts and my_discounts.count() == 0):
            my_discounts = discounts.filter(percent__lte = 60, percent__gt = 50)
        if 25 <= poll_count < 30 or (my_discounts and my_discounts.count() == 0):
            my_discounts = discounts.filter(percent__lte = 50, percent__gt = 40)
        if 20 <= poll_count < 25 or (my_discounts and my_discounts.count() == 0):
            my_discounts = discounts.filter(percent__lte = 40, percent__gt = 30)
        if 15 <= poll_count < 20 or (my_discounts and my_discounts.count() == 0):
            my_discounts = discounts.filter(percent__lte = 30, percent__gt = 20)
        if 10 <= poll_count < 15 or (my_discounts and my_discounts.count() == 0):
            my_discounts = discounts.filter(percent__lte = 20, percent__gt = 10)
        if poll_count < 10 or (my_discounts and my_discounts.count() == 0):
            my_discounts = discounts.filter(percent__lte = 10)
        if my_discounts.count() == 0:
            return Response({
                'result': False,
                'message': 'تخفیفی برای این فروشگاه یافت نشد.'
            })
        print('possible discounts:')
        print(my_discounts)
        import random
        index = random.randint(0, len(my_discounts) - 1)
        product = my_discounts[index]
        code = ''.join(random.choices(string.ascii_uppercase + string.digits + string.ascii_lowercase, k = 5))
        while Discount.objects.filter(code = code).count() != 0:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits + string.ascii_lowercase, k = 5))
        discount = Discount.objects.create(code = code, active = True, candidate_product = product, customer = customer)
        product.count -= 1
        product.save()
        serializer = DiscountSerializer(discount)
        return Response({
            'result': True,
            'message': 'تخفیف مورد نظر به کاربر تخصیص داده شد.',
            'discount': serializer.data
        })


# noinspection DjangoOrm, PyMethodMayBeStatic
class MyPolls(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request) -> Response:
        """
        Gives the incomplete polls to customer.
        @param request: Containing I{phone_number} of customer.
        @return: Response having all incomplete polls of customer.
        """
        customer = Customer.objects.filter(user__phone_number = request.data['phone_number'], user = request.user)
        if customer.count() == 0:
            return Response({
                'result': False,
                'message': 'دسترسی رد شد.'
            })
        customer = customer[0]
        all_polls = Poll.objects.filter(Q(paragraph_poll__paragraph_poll_answers__customer = customer,
                                          paragraph_poll__paragraph_poll_answers__poll_answer__completed = False) |
                                        Q(short_answer_poll__short_answer_poll_answers__customer = customer,
                                          short_answer_poll__short_answer_poll_answers__poll_answer__completed = False) |
                                        Q(linear_scale_poll__linear_scale_poll_answers__customer = customer,
                                          linear_scale_poll__linear_scale_poll_answers__poll_answer__completed = False) |
                                        Q(check_box_poll__check_box_poll_answers__customer = customer,
                                          check_box_poll__check_box_poll_answers__poll_answer__completed = False) |
                                        Q(multiple_choice_poll__multiple_choice_answers__customer = customer,
                                          multiple_choice_poll__multiple_choice_answers__poll_answer__completed = False))
        data = {
            'result': True,
            'message': 'نظرسنجی های یک کاربر',
            'polls': []
        }
        for poll in all_polls:
            data_poll = {
                'id': poll.pk,
                'text': poll.text,
                'shop': poll.shop.name,
                'importance': poll.importance,
                'expire_date': poll.expire_date,
                'type_poll': poll.type_poll
            }
            if poll.type_poll == "LinearScalePoll":
                linear_poll = poll.linear_scale_poll
                data_poll.update({
                    'choices_count': linear_poll.choices_count,
                    'start': linear_poll.start,
                    'step': linear_poll.step

                })
            elif poll.type_poll == 'MultipleChoicePoll':
                choices = []
                for option in poll.multiple_choice_poll.options.all():
                    choices.append(option.answer_text)
                data_poll.update({'choices': choices})
            else:
                choices = []
                for option in poll.check_box_poll.options.all():
                    choices.append(option.answer_text)
                data_poll.update({'choices': choices})
            data['polls'].append(data_poll)
        return Response(data = data)


# noinspection PyMethodMayBeStatic
class PollToCustomer(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)

    def post(self, request) -> Response:
        """
        Assigns a poll to customer.
        @param request: Containing shop and customer's phone number.
        @return: A Response having random poll assigned to customer, if any exists.
        """
        shop = Shop.objects.get(pk = request.data['shop'])
        shops = request.user.salesman.shops
        if shops.filter(pk = shop.pk).count() == 0:
            return Response({
                'result': False,
                'message': 'دسترسی رد شد.'
            })
        customer = Customer.objects.get(user__phone_number = request.data['phone_number'])
        my_polls = Poll.objects.filter(Q(paragraph_poll__paragraph_poll_answers__customer = customer,
                                         paragraph_poll__paragraph_poll_answers__poll_answer__completed = True) |
                                       Q(short_answer_poll__short_answer_poll_answers__customer = customer,
                                         short_answer_poll__short_answer_poll_answers__poll_answer__completed = True) |
                                       Q(linear_scale_poll__linear_scale_poll_answers__customer = customer,
                                         linear_scale_poll__linear_scale_poll_answers__poll_answer__completed = True) |
                                       Q(check_box_poll__check_box_poll_answers__customer = customer,
                                         check_box_poll__check_box_poll_answers__poll_answer__completed = True) |
                                       Q(multiple_choice_poll__multiple_choice_answers__customer = customer,
                                         multiple_choice_poll__multiple_choice_answers__poll_answer__completed = True))
        print("my pollls:")
        print(my_polls)
        not_my_polls = Poll.objects.filter((~Q(paragraph_poll__paragraph_poll_answers__customer = customer) &
                                            ~Q(short_answer_poll__short_answer_poll_answers__customer = customer) &
                                            ~Q(linear_scale_poll__linear_scale_poll_answers__customer = customer) &
                                            ~Q(check_box_poll__check_box_poll_answers__customer = customer) &
                                            ~Q(multiple_choice_poll__multiple_choice_answers__customer = customer)),
                                           shop = shop)
        print("not my polls:")
        print(not_my_polls)
        poll_count = my_polls.filter(shop = shop).count()
        print(not_my_polls.all().count())
        polls = None
        if 50 <= poll_count:
            polls = not_my_polls.filter(importance = 10, expire_date__gte = timezone.now())
        if 45 <= poll_count < 50 or (polls and polls.count() == 0):
            polls = not_my_polls.filter(importance = 9, expire_date__gte = timezone.now())
        if 40 <= poll_count < 45 or (polls and polls.count() == 0):
            polls = not_my_polls.filter(importance = 8, expire_date__gte = timezone.now())
        if 35 <= poll_count < 40 or (polls and polls.count() == 0):
            polls = not_my_polls.filter(importance = 7, expire_date__gte = timezone.now())
        if 30 <= poll_count < 35 or (polls and polls.count() == 0):
            polls = not_my_polls.filter(importance = 6, expire_date__gte = timezone.now())
        if 25 <= poll_count < 30 or (polls and polls.count() == 0):
            polls = not_my_polls.filter(importance = 5, expire_date__gte = timezone.now())
        if 20 <= poll_count < 25 or (polls and polls.count() == 0):
            polls = not_my_polls.filter(importance = 4, expire_date__gte = timezone.now())
        if 15 <= poll_count < 20 or (polls and polls.count() == 0):
            polls = not_my_polls.filter(importance = 3, expire_date__gte = timezone.now())
        if 10 <= poll_count < 15 or (polls and polls.count() == 0):
            polls = not_my_polls.filter(importance = 2, expire_date__gte = timezone.now())
        if poll_count < 10 or (polls and polls.count() == 0):
            polls = not_my_polls.filter(importance = 1, expire_date__gte = timezone.now())
        if polls.count() == 0:
            return Response({
                'result': False,
                'message': 'نظرسنجی ای یافت نشد.'
            })
        print("possible polls:")
        print(polls)
        import random
        index = random.randint(0, len(polls) - 1)
        print("len:")
        print(len(polls))
        print("index:")
        print(index)
        poll = polls[index]
        print(type(polls[index]))
        poll_answer = PollAnswer.objects.create(completed = False)
        if poll.type_poll == 'LinearScalePoll':
            print(poll.linear_scale_poll)
            LinearScalePollAnswer.objects.create(poll = poll.linear_scale_poll, customer = customer,
                                                 poll_answer = poll_answer)
        elif poll.type_poll == 'CheckBoxPoll':
            print(poll.check_box_poll)
            CheckBoxPollAnswer.objects.create(check_box_poll = poll.check_box_poll, customer = customer,
                                              poll_answer = poll_answer)
        elif poll.type_poll == 'MultipleChoicePoll':
            print(poll.multiple_choice_poll)
            MultipleChoiceAnswer.objects.create(multiple_choice = poll.multiple_choice_poll, customer = customer,
                                                poll_answer = poll_answer)
        elif poll.type_poll == 'ShortAnswerPoll':
            print(poll.short_answer_poll)
            ShortAnswerPollAnswer.objects.create(poll = poll.short_answer_poll, customer = customer,
                                                 poll_answer = poll_answer)
        elif poll.type_poll == 'ParagraphPoll':
            print(poll.paragraph_poll)
            ParagraphPollAnswer.objects.create(poll = poll.paragraph_poll, customer = customer,
                                               poll_answer = poll_answer)
        return Response({
            'result': True,
            'message': 'نظرسنجی به کاربر داده شد.',
        })


# noinspection PyMethodMayBeStatic
class EditShop(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)

    def post(self, request) -> Response:
        """
        Edits a shop.
        @param request: Containing information wanted to edit.
        @return: Response showing whether editing was successful or not.
        """
        shop = Shop.objects.get(pk = request.data['shop'])
        shops = request.user.salesman.shops
        if shops.filter(pk = shop.pk).count() == 0:
            return Response({
                'result': False,
                'message': 'دسترسی رد شد.'
            })
        serializer = ShopSerializer(shop, data = request.data, partial = True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'result': True,
                'message': 'ویرایش فروشگاه با موفقیت انجام شد.'
            })
        else:
            print(serializer.errors)
            return Response({
                'result': False,
                'message': 'ویرایش فروشگاه با خطا مواجه شد.'
            })


# noinspection PyUnusedLocal, PyMethodMayBeStatic
class GetShops(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request) -> Response:
        """
        Gets all shops.
        @param request: Unused.
        @return: Response having all shops.
        """
        shops = None
        if 'shop_kind' in request.data:
            shops = Shop.objects.filter(shop_kind_id = request.data['shop_kind'])
        if 'name' in request.data:
            if shops:
                shops = shops.filter(name__contains = request.data['name'])
            else:
                shops = Shop.objects.filter(name__contains = request.data['name'])
        if not shops and 'shop_kind' not in request.data and 'name' not in request.data:
            shops = Shop.objects.all()
        data = []
        for shop in shops:
            serializer = GetShopSerializer(shop)
            data.append(serializer.data)
        if data:
            return Response({
                'result': True,
                'message': 'فروشگاه ها',
                'shops': data
            })
        else:
            return Response({
                'result': False,
                'message': 'فروشگاهی یافت نشد.'
            })


# noinspection PyMethodMayBeStatic
class LogoutViewCustomer(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        """
        Logs a customer out.
        @param request: Customer to be logged out.
        @return: Always True.
        """
        token = Token.objects.get(user = request.user)
        token.delete()
        return Response({
            'result': True,
            'message': 'با موفقیت خارج شد.'
        })


class LogoutViewSalesman(LogoutView):
    authentication_classes = (SessionAuthentication,)


# noinspection PyMethodMayBeStatic
class GetShopById(APIView):
    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request) -> Response:
        """
        Gives shop information.
        @param request: Requested shop id.
        @return: Response having shop information.
        """
        shop = Shop.objects.get(pk = request.data['shop'])
        shops = request.user.salesman.shops
        if shops.filter(pk = shop.pk).count() == 0:
            return Response({
                'result': False,
                'message': 'دسترسی رد شد.'
            })
        shop_kind = ShopKind.objects.get(pk = shop.shop_kind_id)
        serializer = ShopKindSerializer(shop)
        serializer.data.update({'shop_kind': shop_kind.name})
        return Response({
            'result': True,
            'message': serializer.data
        })
