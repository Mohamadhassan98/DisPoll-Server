import string

from django.contrib.auth import login
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from drf_autodocs.decorators import format_docstring
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from silk.profiling.profiler import silk_profile

from Tick_server import docs, responses
from Tick_server.docs import *
from Tick_server.responses import *
from Tick_server.serializers import *


# noinspection PyMethodMayBeStatic
@format_docstring(customer_signup_first, response_example = docs.phone_added_successfully)
class SignUpFirstCustomer(APIView):
    """
    Gets and saves new customers

    Request{}
    Response{response_example}
    """
    serializer_class = PhoneSerializer
    response_serializer_class = ResponseSerializer

    # @FullyTested
    @silk_profile()
    def post(self, request) -> Response:

        if not request.user.is_superuser:
            return Response(access_denied)
        if 'phone_number' not in request.data:
            return Response(insufficient_data)
        phone = request.data['phone_number']
        if Customer.objects.filter(user__phone_number = phone).count() == 1:
            return Response(customer_already_exists)
        else:
            Code4Digit.objects.update_or_create(phone_number = phone, defaults = {'code': '1111'})
            return Response(responses.phone_added_successfully)


# noinspection PyMethodMayBeStatic
@format_docstring(customer_signup_second, resp = customer_signup_successful)
class SignUpSecondCustomer(APIView):
    # @FullyTested
    """
    Gets phone number and code sent to user and checks if it's valid

    Request{}
    Response{resp}
    """
    serializer_class = Code4DigitSerializer
    response_serializer_class = ResponseSerializer

    @silk_profile()
    def post(self, request) -> Response:
        if not request.user.is_superuser:
            return Response(access_denied)
        if 'phone_number' not in request.data or 'code' not in request.data:
            return Response(insufficient_data)
        phone = request.data['phone_number']
        code = request.data['code']
        if Code4Digit.objects.filter(phone_number = phone, code = code).count() == 1:
            return Response(signup_successful)
        else:
            return Response(code_incorrect)


# noinspection PyMethodMayBeStatic
@format_docstring(customer_signup_first, resp = docs.code_resent)
class ResendCodeCustomer(APIView):
    """
    Gets phone number and sends a new code to that number

    Request{}
    Response{resp}
    """
    serializer_class = PhoneSerializer
    response_serializer_class = ResponseSerializer

    # @FullyTested
    @silk_profile()
    def post(self, request) -> Response:
        if not request.user.is_superuser:
            return Response(access_denied)
        if 'phone_number' not in request.data:
            return Response(insufficient_data)
        phone = request.data['phone_number']
        codes = Code4Digit.objects.filter(phone_number = phone)
        if codes.count() == 0:
            return Response(customer_code_resend_failed)
        codes.update(code = '1111')
        return Response(code_resent)


# noinspection PyMethodMayBeStatic
@format_docstring(customer_signup_final, resp = customer_signup_successful2)
class SignUpFinalCustomer(APIView):
    """
    Gets phone number and other information to sign up a user.

    Request{}
    Response{resp}
    """
    serializer_class = docs.CustomerSerializer
    response_serializer_class = ResponseWithTokenSerializer

    # @FullyTested
    @silk_profile()
    def post(self, request) -> Response:
        if not request.user.is_superuser:
            return Response(access_denied)
        if 'phone_number' not in request.data:
            return Response(insufficient_data)
        copy = request.data.copy()
        copy.update({'user_type': 'CU'})
        serializer = UserSerializer(data = copy)
        code = Code4Digit.objects.filter(phone_number = copy['phone_number'])
        if not serializer.is_valid():
            print(serializer.errors)
            return Response(signup_failed)
        if code.count() == 0:
            print('invalid phone_number specified')
            return Response(signup_failed)
        else:
            user = serializer.save()
            Customer.objects.create(user = user)
            token, _ = Token.objects.get_or_create(user = user)
            code[0].delete()
            response = signup_successful.copy()
            response.update({'token': token.key})
            return Response(response)


# noinspection PyMethodMayBeStatic
@format_docstring(customer_login, resp = customer_login_successful)
class LoginCustomer(APIView):
    """
    Gets phone number and login credentials of a user and tries to login that user

    Request{}
    Response{resp}
    """
    serializer_class = LoginSerializer
    response_serializer_class = ResponseWithUserSerializer

    # @FullyTested
    @silk_profile()
    def post(self, request) -> Response:
        if not request.user.is_superuser:
            return Response(access_denied)
        if 'phone_number' not in request.data or 'password' not in request.data:
            return Response(insufficient_data)
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
        copy = serializer.data.copy()
        copy.pop('password')
        copy.pop('user_type')
        result = customer_login_successful.copy()
        result.update({'customer_info': copy})
        result.update({'token': token.key})
        return Response(result)


# noinspection PyMethodMayBeStatic
@format_docstring(customer_edit_pro, resp = edit_pro_successful)
class EditCustomerProfile(APIView):
    """
    Authenticates the user, validates and changes the information he sends via request.

    Request{}
    Response{resp}
    """
    serializer_class = EditProSerializer
    response_serializer_class = ResponseSerializer

    # @FullyTested
    @silk_profile()
    def post(self, request) -> Response:
        if 'phone_number' not in request.data:
            return Response(insufficient_data)
        customer = Customer.objects.filter(user__phone_number = request.data['phone_number'],
                                           user__username = request.user.username)
        _mutable = request.data._mutable
        request.data._mutable = True
        if customer.count() == 0 or request.user.is_superuser:
            return Response(access_denied)
        customer = customer[0]
        if 'old_password' in request.data:
            old_password = request.data.pop('old_password')
            if not customer.check_password(old_password[0]):
                return Response(customer_wrong_old_password)
        serializer = UserUpdateSerializer(customer.user, data = request.data, partial = True)
        if not serializer.is_valid():
            print(serializer.errors)
            return Response(customer_edit_profile_failed)
        else:
            serializer.save()
            return Response(customer_edit_profile_successful)


# noinspection PyMethodMayBeStatic
@format_docstring(salesman_signup_first, resp = email_added_successfully)
class SignUpFirstSalesman(APIView):
    """
    Gets and saves new salesman email and password

    Request{}
    Response{resp}
    """
    serializer_class = EmailSerializer
    response_serializer_class = ResponseSerializer

    permission_classes = (AllowAny,)
    authentication_classes = []

    @silk_profile()
    def post(self, request) -> Response:
        if 'email' not in request.data or 'password' not in request.data:
            return Response(insufficient_data)
        email = request.data['email']
        password = request.data['password']
        if Salesman.objects.filter(user__email = email).count() == 1:
            return Response(salesman_already_exists)
        else:
            Code4DigitSalesman.objects.update_or_create(email = email, password = password, defaults = {'code': '1111'})
            return Response(email_saved_successfully)


# noinspection PyMethodMayBeStatic
@format_docstring(salesman_signup_second, resp = salesman_signup_successful)
class SignUpSecondSalesman(APIView):
    """
    Gets email and code sent to user and checks if it's valid

    Request{}
    Response{resp}
    """
    permission_classes = (AllowAny,)
    authentication_classes = []

    serializer_class = SalesmanCode4DigitSerializer
    response_serializer_class = ResponseSerializer

    @silk_profile()
    def post(self, request) -> Response:
        if 'email' not in request.data or 'code' not in request.data:
            return Response(insufficient_data)
        email = request.data['email']
        code = request.data['code']
        if Code4DigitSalesman.objects.filter(email = email, code = code).count() == 1:
            return Response(signup_successful)
        else:
            return Response(code_incorrect)


# noinspection PyMethodMayBeStatic
@format_docstring(salesman_signup_final, resp = salesman_signup_successful2)
class SignUpFinalSalesman(APIView):
    """
    Gets email and other information to sign up a user.

    Request{}
    Response{resp}
    """
    serializer_class = SalesmanInfoSerializer
    response_serializer_class = ResponseWithTokenSerializer

    permission_classes = (AllowAny,)
    authentication_classes = []

    @transaction.atomic
    def post(self, request) -> Response:
        if 'email' not in request.data:
            return Response(insufficient_data)
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
                token, _ = Token.objects.get_or_create(user = user)
                result = signup_successful.copy()
                result.update({'token': token.key})
                return Response(result)
        except serializers.ValidationError as e:
            print(e)
            return Response(signup_failed)


# noinspection PyMethodMayBeStatic
@format_docstring(salesman_email, resp = docs.code_resent)
class ResendCodeSalesman(APIView):
    """
    Gets email and sends a new code to that email

    Request{}
    Response{resp}
    """

    serializer_class = EmailSerializer
    response_serializer_class = ResponseSerializer

    permission_classes = (AllowAny,)
    authentication_classes = []

    @silk_profile()
    def post(self, request) -> Response:
        if 'email' not in request.data:
            return Response(insufficient_data)
        email = request.data['email']
        Code4DigitSalesman.objects.filter(email = email).update(code = '1111')
        return Response(code_resent)


# noinspection PyMethodMayBeStatic
@format_docstring(salesman_login, resp = salesman_login_successful)
class LoginSalesman(APIView):
    """
    Gets email or username and login credentials of a user and tries to login that user

    Request{}
    Response{resp}
    """
    permission_classes = (AllowAny,)
    authentication_classes = []

    serializer_class = EmailSerializer

    response_serializer_class = LoginSalesmanSerializer

    @silk_profile()
    def post(self, request) -> Response:
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
        token, _ = Token.objects.get_or_create(user = user)
        shops = salesman[0].shops.all()
        shops_list = []
        for shop in shops:
            shops_list.append({'id': shop.id, 'name': shop.name})
        copy.update({'first_name': user.first_name, 'last_name': user.last_name, 'shops': shops_list})
        return Response({
            'result': True,
            'message': 'ورود با موفقیت انجام شد.',
            'salesman': copy,
            'token': token.key
        })


# noinspection PyMethodMayBeStatic
@format_docstring(profile_edit_pro, resp = edit_pro_successful)
class EditSalesmanProfileView(APIView):
    @transaction.atomic
    @silk_profile()
    def post(self, request) -> Response:
        """
        Authenticates the user, validates and changes the information he sends via I{request}.
        @param request: Containing information wanted to edit.
        @return: I{Response} showing whether information updated or not.
        """
        salesman = Salesman.objects.filter(user__email = request.data['email'], user = request.user)
        if salesman.count() == 0:
            return Response(access_denied)
        salesman = salesman[0]
        if 'old_password' in request.data:
            old_password = request.data.pop('old_password')
            if not salesman.check_password(old_password[0]):
                return Response({
                    'result': False,
                    'message': 'رمز وارد شده صحیح نیست.'
                })
        try:
            with transaction.atomic():
                serializer = UserUpdateSerializer(salesman.user, request.data, partial = True)
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
class AddShop(APIView):
    @silk_profile()
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
    @silk_profile()
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
    @silk_profile()
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
    @silk_profile()
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
    permission_classes = (AllowAny,)
    authentication_classes = []

    @silk_profile()
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
    permission_classes = (AllowAny,)
    authentication_classes = []

    @silk_profile()
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


# # noinspection PyMethodMayBeStatic
# class GetSalesmanAvatar(APIView):
#     def get(self, request) -> FileResponse:
#         """
#         Gets the I{avatar} of salesman.
#         @param request: containing authenticated user object.
#         @return: FileResponse containing salesman's I{avatar}
#         """
#         file = File(open('new-temp/' + str(request.user.salesman.avatar), 'rb'))
#         return FileResponse(file)
#
#
# noinspection PyMethodMayBeStatic
# class GetShopPicture(APIView):
#     permission_classes = (IsAuthenticated,)
#     authentication_classes = (SessionAuthentication,)
#
#     def post(self, request) -> Union[Response, FileResponse]:
#         """
#         Gets the I{picture} of shop.
#         @param request: containing shop's I{pk}.
#         @return: FileResponse containing shop's I{picture} or Response if access is denied.
#         """
#         shop = Shop.objects.get(pk = request.data['shop'])
#         shops = request.user.salesman.shops
#         if shops.filter(pk = shop.pk).count() == 0:
#             return Response({
#                 'result': False,
#                 'message': 'دسترسی رد شد.'
#             })
#         file = File(open('new-temp/' + str(shop.picture)), 'rb')
#         return FileResponse(file)
#
#
# noinspection PyMethodMayBeStatic
# class GetShopBusinessLicense(APIView):
#     permission_classes = (IsAuthenticated,)
#     authentication_classes = (SessionAuthentication,)
#
#     def post(self, request) -> Union[Response, FileResponse]:
#         """
#         Gets the I{business_license} of shop.
#         @param request: containing shop's I{pk}.
#         @return: FileResponse containing shop's I{business_license} or Response if access is denied.
#         """
#         shop = Shop.objects.get(pk = request.data['shop'])
#         shops = request.user.salesman.shops
#         if shops.filter(pk = shop.pk).count() == 0:
#             return Response({
#                 'result': False,
#                 'message': 'دسترسی رد شد.'
#             })
#         file = File(open('new-temp/' + str(shop.business_license)), 'rb')
#         return FileResponse(file)
#
#
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
    @transaction.atomic
    @silk_profile()
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
                    paragraph_serializer.save()
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
                    short_answer_serializer.save()
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
    @silk_profile()
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


# noinspection PyMethodMayBeStatic
class MyPolls(APIView):
    @silk_profile()
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
                                          paragraph_poll__paragraph_poll_answers__poll_answer__completed = False,
                                          expire_date__gte = timezone.now()) |
                                        Q(short_answer_poll__short_answer_poll_answers__customer = customer,
                                          short_answer_poll__short_answer_poll_answers__poll_answer__completed = False,
                                          expire_date__gte = timezone.now()) |
                                        Q(linear_scale_poll__linear_scale_poll_answers__customer = customer,
                                          linear_scale_poll__linear_scale_poll_answers__poll_answer__completed = False,
                                          expire_date__gte = timezone.now()) |
                                        Q(check_box_poll__check_box_poll_answers__customer = customer,
                                          check_box_poll__check_box_poll_answers__poll_answer__completed = False,
                                          expire_date__gte = timezone.now()) |
                                        Q(multiple_choice_poll__multiple_choice_answers__customer = customer,
                                          multiple_choice_poll__multiple_choice_answers__poll_answer__completed = False,
                                          expire_date__gte = timezone.now()))
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
            elif poll.type_poll == 'CheckBoxPoll':
                choices = []
                for option in poll.check_box_poll.options.all():
                    choices.append(option.answer_text)
                data_poll.update({'choices': choices})
            data['polls'].append(data_poll)
        return Response(data = data)


# noinspection PyMethodMayBeStatic
class PollToCustomer(APIView):
    @silk_profile()
    def post(self, request) -> Response:
        """
        Assigns a poll to customer.
        @param request: Containing shop and customer's phone number.
        @return: A Response having random poll assigned to customer, if any exists.
        """
        phone_number = request.data['phone_number']
        if Customer.objects.filter(user__phone_number = phone_number).count() == 0:
            return Response({
                'result': False,
                'message': 'کاربری با این شماره یافت نشد'
            })
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
    @silk_profile()
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


# noinspection PyMethodMayBeStatic, PyUnboundLocalVariable
class GetShops(APIView):
    @silk_profile()
    def post(self, request) -> Response:
        """
        Gets all shops.
        @param request: Unused.
        @return: Response having all shops.
        """
        if not request.user.is_superuser:
            return Response(access_denied)
        shops = []
        if 'shop_kinds' in request.data:
            shop_kinds = request.data['shop_kinds'][1:-1].split(',')
        page = int(request.data['page'])
        offset = int(request.data['offset'])
        if 'shop_kinds' in request.data and 'name' not in request.data:
            for shop_kind in shop_kinds:
                shops_filter = Shop.objects.filter(shop_kind__name = shop_kind)
                for shop in shops_filter:
                    shops.append(shop)
            shops = shops[page * offset: page * offset + offset]
        if 'name' in request.data and 'shop_kinds' not in request.data:
            shops = Shop.objects.filter(name__contains = request.data['name'])[page * offset: page * offset + offset]
        if 'shop_kinds' not in request.data and 'name' not in request.data:
            shops = Shop.objects.all()[page * offset: page * offset + offset]
        if 'shop_kinds' in request.data and 'name' in request.data:
            for shop_kind in shop_kinds:
                shops_filter = Shop.objects.filter(shop_kind__name = shop_kind, name__contains = request.data['name'])
                for shop in shops_filter:
                    shops.append(shop)
            shops = shops[page * offset: page * offset + offset]
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
                'result': True,
                'message': 'فروشگاهی یافت نشد.'
            })


# noinspection PyMethodMayBeStatic
class LogoutViewCustomer(APIView):
    @silk_profile()
    def post(self, request):
        """
        Logs a customer out.
        @param request: Customer to be logged out.
        @return: Always True.
        """
        if request.user.is_superuser or request.user.user_type == 'SM':
            return Response(access_denied)
        token = Token.objects.filter(user = request.user)
        if token.count() != 0:
            token.delete()
        return Response({
            'result': True,
            'message': 'با موفقیت خارج شد.'
        })


# noinspection PyMethodMayBeStatic
class LogoutViewSalesman(APIView):
    @silk_profile()
    def post(self, request):
        """
        Logs a Salesman out.
        @param request: Salesman to be logged out.
        @return: Always True.
        """
        if request.user.is_superuser or request.user.user_type == 'CU':
            return Response(access_denied)
        token = Token.objects.filter(user = request.user)
        if token.count() != 0:
            token.delete()
        return Response({
            'result': True,
            'message': 'با موفقیت خارج شد.'
        })


# noinspection PyMethodMayBeStatic
class GetShopById(APIView):
    @silk_profile()
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
        serializer = ShopSerializer(shop)
        serializer.data.update({'shop_kind': shop_kind.name})
        return Response({
            'result': True,
            'message': serializer.data
        })


# noinspection PyMethodMayBeStatic
class Statistics(APIView):
    @silk_profile()
    def post(self, request):
        salesman = request.user.salesman
        shops = Shop.objects.filter(salesman = salesman)
        poll = Poll.objects.get(id = request.data['poll_id'])
        if shops.filter(id = poll.shop_id).count() == 0:
            return Response(access_denied)
        if poll.type_poll == 'ShortAnswerPoll':
            answers = []
            short_poll_answers = ShortAnswerPollAnswer.objects.filter(poll__poll = poll)
            for answer in short_poll_answers:
                answers.append(answer.answer_text)
            return Response({
                'result': True,
                'message': 'پاسخ های کوتاه',
                'all_answers': answers
            })
        elif poll.type_poll == 'ParagraphPoll':
            answers = []
            paragraph_poll_answers = ParagraphPollAnswer.objects.filter(poll__poll = poll)
            for answer in paragraph_poll_answers:
                answers.append(answer.answer_text)
            return Response({
                'result': True,
                'message': 'جواب های نظرسنجی',
                'all_answers': answers
            })
        elif poll.type_poll == 'LinearScalePoll':
            total_submissions = 0
            start = poll.linear_scale_poll.start
            step = poll.linear_scale_poll.step
            count = poll.linear_scale_poll.choices_count
            possible_answers = {}
            cnt = 0
            while count:
                possible_answers[start + step * cnt] = 0
                count -= 1
                cnt += 1
            linear_scale_answers = LinearScalePollAnswer.objects.filter(poll__poll = poll)
            for answer in linear_scale_answers:
                total_submissions += 1
                possible_answers[answer.answer] += 1
            data = {
                'result': True,
                'message': 'جواب های نظرسنجی',
                'total_submission': total_submissions
            }
            index = 1
            for key, value in possible_answers.items():
                tmp = 'option_' + str(index)
                index += 1
                data.update({tmp: value})
            return Response(data = data)
        elif poll.type_poll == 'MultipleChoicePoll':
            multiple_choice_poll = poll.multiple_choice_poll
            multiple_choice_answers = MultipleChoiceAnswer.objects.filter(multiple_choice__poll = poll)
            possible_answers = {}
            options = multiple_choice_poll.options.all()
            total_submissions = 0
            for option in options:
                possible_answers[option.answer_text] = 0
            for answer in multiple_choice_answers:
                total_submissions += 1
                possible_answers[answer.option.answer_text] += 1
            data = {
                'result': True,
                'message': 'جواب های نظرسنجی',
                'total_submissions': total_submissions
            }
            index = 0
            for key, value in possible_answers.items():
                tmp = 'option_' + str(index)
                index += 1
                data.update({tmp: value})
            return Response(data = data)
        elif poll.type_poll == 'CheckBoxPoll':
            check_box_poll = poll.check_box_poll
            check_box_answers = CheckBoxPollAnswer.objects.filter(check_box_poll__poll = poll)
            options = check_box_poll.options.all()
            possible_answers = {}
            total_submissions = 0
            for option in options:
                possible_answers[option.answer_text] = 0
            for answer in check_box_answers:
                options = answer.options.all()
                print(options)
                for option in options:
                    total_submissions += 1
                    possible_answers[option.answer_text] += 1
                print(possible_answers)
            data = {
                'result': True,
                'message': 'جواب های نظرسنجی',
                'total_submissions': total_submissions
            }
            index = 0
            for key, value in possible_answers.items():
                tmp = 'option_' + str(index)
                index += 1
                data.update({tmp: value})
            return Response(data = data)


# noinspection PyMethodMayBeStatic
class AddAdvertise(APIView):
    @silk_profile()
    def post(self, request):
        shop = Shop.objects.filter(pk = request.data['shop'], salesman__user = request.user)
        if shop.count() == 0:
            return Response(access_denied)
        serializer = AdvertisementSerializer(data = request.data)
        if not serializer.is_valid():
            print(serializer.errors)
            return Response({
                'result': False,
                'message': 'اضافه کردن تبلیغ با خطا مواجه شد.'
            })
        else:
            serializer.save()
            return Response({
                'result': True,
                'message': 'اضافه کردن تبلیغ با موفقیت انجام شد.'
            })


# noinspection PyMethodMayBeStatic
class GetAds(APIView):
    @silk_profile()
    def get(self, request):
        advertisements = Advertisement.objects.all()
        ads = []
        for ad in advertisements:
            serializer = GetAdvertisementSerializer(ad)
            ads.append(serializer.data)
        return Response({
            'result': True,
            'message': 'تبلیغ ها',
            'ads': ads
        })


# noinspection PyMethodMayBeStatic
class ApplyDiscount(APIView):
    @silk_profile()
    def post(self, request):
        discount = Discount.objects.filter(candidate_product__shop__salesman__user = request.user,
                                           pk = request.data['discount_id'])
        if discount.count() == 0:
            return Response(access_denied)
        discount = discount[0]
        discount.active = False
        discount.save()
        return Response({
            'result': True,
            'message': 'تخفیف اعمال شد.'
        })


# noinspection PyMethodMayBeStatic
class SalesmanShops(APIView):
    @silk_profile()
    def get(self, request):
        shops = Shop.objects.filter(salesman = request.user.salesman)
        serializer = ShopSerializer(shops, many = True)
        return Response({
            'result': True,
            'message': 'لیست فروشگاه ها',
            'shops': serializer.data
        })


# noinspection PyMethodMayBeStatic
# TODO
class SalesmanPolls(APIView):
    @silk_profile()
    def get(self, request):
        data = {
            'result': True,
            'message': 'لیست نظرسنجی ها',
            'polls': []
        }
        polls = Poll.objects.filter(shop__salesman = request.user.salesman)
        print(polls)
        for poll in polls:
            if poll.type_poll == 'LinearScalePoll':
                linear_scale_poll = poll.linear_scale_poll
                data['polls'].append({
                    'text': poll.text,
                    'start': linear_scale_poll.start,
                    'step': linear_scale_poll.step,
                    'choices_count': linear_scale_poll.choices_count,
                    'poll_id': poll.id
                })
            elif poll.type_poll == 'MultipleChoicePoll':
                # serializer = MultipleChoicePollSerializer(poll.multiple_choice_poll)
                tmp = {
                    'text': poll.text,
                    'options': [],
                    'poll_id': poll.id
                }
                index = 1
                options = poll.multiple_choice_poll.options.all()
                print(options)
                for option in options:
                    option_name = 'option_' + str(index)
                    index += 1
                    tmp['options'].append({option_name: option.answer_text})
                data['polls'].append(tmp)
            elif poll.type_poll == 'CheckBoxPoll':
                serializer = CheckBoxPollSerializer(poll.check_box_poll)
                options = poll.check_box_poll.options.all()
                print(options)
                index = 1
                tmp = {
                    'text': poll.text,
                    'options': [],
                    'poll_id': poll.id
                }
                for option in options:
                    option_name = 'option_' + str(index)
                    index += 1
                    tmp['options'].append({option_name: option.answer_text})
                data['polls'].append(tmp)
            else:
                data['polls'].append({'text': poll.text, 'poll_id': poll.id})
        return Response(data = data)
