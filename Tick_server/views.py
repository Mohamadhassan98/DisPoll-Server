import os
import random
import string

from django.contrib.auth import login
from django.core.files import File
from django.core.files.storage import default_storage
from django.http import FileResponse
from rest_framework.response import Response
from rest_framework.views import APIView

from Tick_server.models import Code4Digit, Customer, Discount, Code4DigitSalesman, Salesman, CustomUser, Shop, \
    CandidateProduct, City, ShopKind
from Tick_server.serializers import DiscountSerializer, PollSerializer, UserSerializer, \
    SalesmanSerializer, ShopSerializer, CandidateProductSerializer, ShopKindSerializer, CitySerializer


# noinspection PyMethodMayBeStatic
class SignUpFirst(APIView):
    def post(self, request) -> Response:
        """
        Gets and saves new customers I{phone_number}
        @param request: includes I{phone_number} only
        @return: Response showing whether saving phone number was successful or not.
        """
        phone = request.data['phone_number']
        if Customer.objects.filter(user__phone_number=phone).count() == 1:
            return Response({
                'result': False,
                'message': 'کاربری با این شماره تلفن قبلاً ثبت‌نام کرده.',
            })
        else:
            Code4Digit.objects.update_or_create(phone_number=phone, defaults={'code': '1111'})
            return Response({
                'result': True,
                'message': 'شماره تلفن با موفقیت ثبت شد.',
            })


# noinspection PyMethodMayBeStatic
class SignUpSecond(APIView):
    def post(self, request) -> Response:
        """
        Gets phone number and code sent to user and checks if it's valid
        @param request: includes phone number and code
        @return: Response showing whether the code is valid and sign up is successful or not
        """
        phone = request.data['phone_number']
        code = request.data['code']
        if Code4Digit.objects.filter(phone_number=phone, code=code).count() == 1:
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
class ResendCode(APIView):
    def post(self, request) -> Response:
        """
        Gets phone number and sends a new code to that number
        @param request: includes phone number only
        @return: Response always contains true
        """
        phone = request.data['phone_number']
        Code4Digit.objects.filter(phone_number=phone).update(code='1111')
        return Response({
            'result': True,
            'message': 'کد مجدداً ارسال شد.',
        })


# noinspection PyMethodMayBeStatic
class SignUpFinal(APIView):
    def post(self, request) -> Response:
        """
        Gets phone number and other information to sign up a user.
        @param request: includes phone number and all necessary information to create new user
        @return: Response showing whether sign up is successful or not
        """
        copy = request.data.copy()
        copy.update({'user_type': 'CU'})
        serializer = UserSerializer(data=copy)
        if not serializer.is_valid():
            print(serializer.errors)
            return Response({
                'result': False,
                'message': 'ثبت‌نام با خطا مواجه شد.',
            })
        else:
            user = serializer.save()
            Customer.objects.create(user=user)
            Code4Digit.objects.get(phone_number=copy['phone_number']).delete()
            return Response({
                'result': True,
                'message': 'ثبت‌نام با موفقیت انجام شد.',
            })


# noinspection PyMethodMayBeStatic
class Login(APIView):
    def post(self, request) -> Response:
        """
        Gets phone number and login credentials of a user and tries to login that user
        @param request: containing phone number and password
        @return: Response showing whether login is successful or not, if login is successful then sends all user
        information
        """
        phone = request.data['phone_number']
        password = request.data['password']
        customer = Customer.objects.filter(user__phone_number=phone)
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
        serializer = UserSerializer(customer[0].user)
        return Response({
            'result': True,
            'message': 'ورود با موفقیت انجام شد.',
            'customer_info': serializer.data
        })


# noinspection PyMethodMayBeStatic
class EditCustomerProfile(APIView):
    def put(self, request, pk) -> Response:
        customer = Customer.objects.get(pk=pk)
        copy = request.data.copy()
        copy.update({'user_type': 'CU'})
        serializer = UserSerializer(customer.user, data=copy)
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
                'salesman': serializer.data
            })


# noinspection PyMethodMayBeStatic
class SignUpFirstSalesman(APIView):
    def post(self, request) -> Response:
        """
        Gets and saves new salesman email and password
        @param request: includes email and password
        @return: Response showing whether saving email and password was successful or not.
        """
        email = request.data['email']
        password = request.data['password']
        if Salesman.objects.filter(user__email=email).count() == 1:
            return Response({
                'result': False,
                'message': 'کاربری با این ایمیل قبلاً ثبت‌نام کرده.',
            })
        else:
            Code4DigitSalesman.objects.update_or_create(email=email, password=password, defaults={'code': '1111'})
            return Response({
                'result': True,
                'message': 'اطلاعات با موفقیت ذخیره شد.',
            })


# noinspection PyMethodMayBeStatic
class SignUpSecondSalesman(APIView):
    def post(self, request) -> Response:
        """
        Gets email and code sent to user and checks if it's valid
        @param request: includes email and code
        @return: Response showing whether the code is valid and sign up is successful or not
        """
        email = request.data['email']
        code = request.data['code']
        if Code4DigitSalesman.objects.filter(email=email, code=code).count() == 1:
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
    def post(self, request) -> Response:
        """
        Gets email and other information to sign up a user.
        @param request: includes email and all necessary information to create new user
        @return: Response showing whether sign up is successful or not
        """
        # print(request.data)
        if 'avatar' in request.data:
            avatar = request.data.pop('avatar')
            file = avatar[0]
            filename = 'SM_' + request.data['username'] + '.jpg'
            with default_storage.open('tmp/' + filename, 'wb') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
                destination.close()
        copy = request.data.copy()
        copy.update({'user_type': 'SM'})
        serializer = UserSerializer(data=copy)
        if not serializer.is_valid():
            print(serializer.errors)
            return Response({
                'result': False,
                'message': 'ثبت‌نام با خطا مواجه شد.'
            })
        user = serializer.save()  # TODO('Wrong logic')
        data = {
            'user': user.pk
        }
        if 'avatar' in request.data:
            data.update({'avatar': default_storage.open('tmp/' + filename, 'rb')})
        serializer = SalesmanSerializer(data=data)
        print(serializer.initial_data)
        if serializer.is_valid():
            serializer.save()
            Code4DigitSalesman.objects.get(email=copy['email']).delete()
            if 'avatar' in request.data:
                os.remove('tmp/' + filename)
            return Response({
                'result': True,
                'message': 'ثبت‌نام با موفقیت انجام شد.',
            })
        else:
            print(serializer.errors)
            return Response({
                'result': False,
                'message': 'ثبت‌نام با خطا مواجه شد.'
            })


# noinspection PyMethodMayBeStatic
class ResendCodeSalesman(APIView):
    def post(self, request) -> Response:
        """
        Gets email and sends a new code to that email
        @param request: includes email only
        @return: Response always contains true
        """
        email = request.data['email']
        Code4DigitSalesman.objects.filter(email=email).update(code='1111')
        return Response({
            'result': True,
            'message': 'کد مجدداً ارسال شد.',
        })


# noinspection PyMethodMayBeStatic
class LoginSalesman(APIView):
    def post(self, request) -> Response:
        """
        Gets email or username and login credentials of a user and tries to login that user
        @param request: containing email or username and password
        @return: Response showing whether login is successful or not, if login is successful then sends all user
        information
        """
        email_field = False
        try:
            email = request.data['email']
            email_field = True
        except KeyError:
            username = request.data['username']

        password = request.data['password']
        if email_field:
            salesman = Salesman.objects.filter(user__email=email)
        else:
            salesman = Salesman.objects.filter(user__username=username)

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


# noinspection PyMethodMayBeStatic
class AddShop(APIView):
    def post(self, request) -> Response:
        """
        Adds a new shop.
        @param request: containing name, address and all other information to add a new shop
        @return: Response showing whether adding a new shop was successful, if adding is successful, then sends shop
        id
        """
        serializer = ShopSerializer(data=request.data)
        if not serializer.is_valid():
            print(serializer.errors)
            return Response({
                'result': False,
                'message': 'اضافه کردن فروشگاه با خطا مواجه شد.'
            })
        else:
            shop = serializer.save()
            print(shop)
            return Response({
                'result': True,
                'message': 'اضافه کردن فروشگاه با موفقیت انجام شد.',
                'shop_id': shop.id
            })


# noinspection PyMethodMayBeStatic
class AddDiscount(APIView):
    def post(self, request) -> Response:
        """
        Adds discount by number of count.
        @param request: containing discount information and count of discount to add
        @return: Response showing whether adding discount is successful or not
        """
        copy = request.data.copy()
        count = int(copy.pop('count')[0])
        print(type(count))
        percent = int(copy.pop('percent')[0])
        exp = int(copy.pop('expire_date')[0])
        copy.update({'count': count})
        copy.update({'percent': percent})
        copy.update({'expire_date': exp})
        serializer = CandidateProductSerializer(data=copy)
        if not serializer.is_valid():
            print(serializer.errors)
            return Response({
                'result': False,
                'message': 'اضافه کردن تخفیف با خطا مواجه شد.'
            })
        else:
            c_product = serializer.save()
            for i in range(copy['count']):
                while True:
                    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                    if Discount.objects.filter(code=code).count() == 0:
                        break
                Discount.objects.create(candidate_product=c_product, code=code)
            return Response({
                'result': True,
                'message': 'اضافه کردن تخفیف با موفقیت انجام شد.'
            })


# noinspection PyMethodMayBeStatic
class ActiveDiscountListView(APIView):
    def post(self, request) -> Response:
        """
        Gets phone number, page and offset and retrieve active discounts list of that customer
        @param request: Containing phone number, page and offset
        @return: Response containing active discounts belong to that customer
        """
        page = int(request.data['page'])
        offset = int(request.data['offset'])
        phone = request.data['phone_number']
        user = CustomUser.objects.get(phone_number=phone)
        discounts = Discount.objects.filter(active=True, customer=Customer.objects.get(user=user))[
                    page * offset: page * offset + offset]
        serializer = DiscountSerializer(discounts, many=True)
        return Response({
            'result': True,
            'message': 'جستجو با موفقیت انجام شد.',
            'discounts': serializer.data
        })


# noinspection PyMethodMayBeStatic
class InactiveDiscountListView(APIView):
    def post(self, request) -> Response:
        """
        Gets phone number, page and offset and retrieve inactive discounts list of that customer
        @param request: Containing phone number, page and offset
        @return: Response containing inactive discounts belong to that customer
        """
        page = int(request.data['page'])
        offset = int(request.data['offset'])
        phone = request.data['phone_number']
        user = CustomUser.objects.get(phone_number=phone)
        discounts = Discount.objects.filter(active=False, customer=Customer.objects.get(user=user))[
                    page * offset: page * offset + offset]
        serializer = DiscountSerializer(discounts, many=True)
        return Response({
            'result': True,
            'message': 'جستجو با موفقیت انجام شد.',
            'discounts': serializer.data
        })


# noinspection PyMethodMayBeStatic
class GetCity(APIView):
    def get(self, pk) -> Response:
        """
        Returns city corresponding requested I{id}.
        @param pk: id for requested city
        @return: Response showing whether city was found or not. If city was found, it will be returned respectively.
        """
        try:
            city = City.objects.get(id=pk)
            serializer = CitySerializer(city)
        except City.DoesNotExist:
            return Response({
                'result': False,
                'message': 'شهر مورد نظر یافت نشد.'
            })
        return Response({
            'result': True,
            'message': serializer.data
        })


# noinspection PyMethodMayBeStatic,PyUnusedLocal
class GetShopKind(APIView):
    def get(self, request, pk) -> Response:
        """
        Returns ShopKind corresponding requested I{id}.
        @param request: Unused
        @param pk: id for requested ShopKind
        @return: Response showing whether ShopKind was found or not. If ShopKind was found, it will be returned
        respectively.
        """
        try:
            shop_kind = ShopKind.objects.get(id=pk)
            serializer = ShopKindSerializer(shop_kind)
        except ShopKind.DoesNotExist:
            return Response({
                'result': False,
                'message': 'نوع فروشگاه مورد نظر یافت نشد.'
            })
        return Response({
            'result': True,
            'message': serializer.data
        })


# TODO program a view that returns all discounts of a salesman
# TODO program a view that allocates a discount to a customer from an specified shop's null customered discounts
class DiscountToCustomer(APIView):
    def post(self, request) -> Response:
        """
        TODO
        :param request:
        :return:
        """
        username = request.data['username']
        customer = Customer.objects.get(user__username=username)
        shop = Shop.objects.get(id=request.data['shop_id'])
        poll_count = customer.linear_scale_poll_answers.filter(shop=shop).count()
        poll_count += customer.short_answer_poll_answers.filter(shop=shop).count()
        poll_count += customer.checkbox_poll_answers.filter(shop=shop).count()
        poll_count += customer.multiple_choice_poll_answers.filter(shop=shop).count()
        poll_count += customer.paragraph_poll_answers.filter(shop=shop).count()
        discounts = CandidateProduct.objects.filter(shop=shop, count__gt=0)
        my_discounts = None
        if 50 <= poll_count:
            my_discounts = discounts.filter(percent__lte=100, percent__gt=90)
        elif 45 <= poll_count < 50 or (my_discounts and my_discounts.count() == 0):
            my_discounts = discounts.filter(percent__lte=90, percent__gt=80)
        elif 40 <= poll_count < 45 or (my_discounts and my_discounts.count() == 0):
            my_discounts = discounts.filter(percent__lte=80, percent__gt=70)
        elif 35 <= poll_count < 40 or (my_discounts and my_discounts.count() == 0):
            my_discounts = discounts.filter(percent__lte=70, percent__gt=60)
        elif 30 <= poll_count < 35 or (my_discounts and my_discounts.count() == 0):
            my_discounts = discounts.filter(percent__lte=60, percent__gt=50)
        elif 25 <= poll_count < 30 or (my_discounts and my_discounts.count() == 0):
            my_discounts = discounts.filter(percent__lte=50, percent__gt=40)
        elif 20 <= poll_count < 25 or (my_discounts and my_discounts.count() == 0):
            my_discounts = discounts.filter(percent__lte=40, percent__gt=30)
        elif 15 <= poll_count < 20 or (my_discounts and my_discounts.count() == 0):
            my_discounts = discounts.filter(percent__lte=30, percent__gt=20)
        elif 10 <= poll_count < 15 or (my_discounts and my_discounts.count() == 0):
            my_discounts = discounts.filter(percent__lte=20, percent__gt=10)
        elif poll_count < 10 or (my_discounts and my_discounts.count() == 0):
            my_discounts = discounts.filter(percent__lte=10)
        else:
            return Response({
                'result': False,
                'message': 'تخفیفی برای این فروشگاه یافت نشد.'
            })
        import random
        product = random.sample(my_discounts, 1)[0]
        discount = Discount.objects.filter(candidate_product=product, customer__isnull=True)[0]
        discount.update(customer=customer, active=True)
        return Response({
            'result': True,
            'message': 'تخفیف مورد نظر به کاربر تخصیص داده شد.'
        })


# noinspection PyMethodMayBeStatic
class EditSalesmanProfileView(APIView):
    def put(self, request, pk, Format=None) -> Response:
        # print(request.databases)
        salesman = Salesman.objects.get(pk=pk)
        copy = request.data.copy()
        if 'avatar' in request.data:
            print("Hoooooray")
            avatar = copy.pop('avatar')
            file = avatar[0]
            filename = 'SM_' + salesman.user.username + '.jpg'
            with default_storage.open('tmp/' + filename, 'wb') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
                destination.close()
        copy.update({'user_type': 'SM'})
        serializer = UserSerializer(salesman.user, data=copy, partial=True)
        if not serializer.is_valid():
            print(serializer.errors)
            return Response({
                'result': False,
                'message': 'ویرایش اطلاعات با خطا مواجه شد.'
            })
        serializer.save()
        # data = {'user': user.pk}
        # if 'avatar' in request.data:
        #     data.update({'avatar':default_storage.open('tmp/' + filename,'rb')})
        # serializer = SalesmanSerializer(salesman, data = data, partial=True)
        # if serializer.is_valid():
        #     serializer.save()
        # for i in range(100000000000):
        #     pass
        # if 'avatar' in request.data:
        #     os.remove('tmp/' + filename)
        # os.remove('tmp/' + filename)
        return Response({
            'result': True,
            'message': 'ویرایش اطلاعات با موفقیت انجام شد.',
        })
        # else:
        #     print(serializer.errors)
        #     return Response({
        #         'result': False,
        #         'message': 'ویرایش اطلاعات با خطا مواجه شد.'
        #     })


class test(APIView):
    def get(self, request, path, Format=None):
        fe = File(open('tmp/' + path, 'rb'))
        return FileResponse(fe)


class NotCompletedPollList(APIView):
    def post(self, request, Format=None):
        page = request.data['post']
        offset = request.data['offset']
        phone = request.data['phone_number']
        customer = Customer.objects.get(phone_number=phone)
        polls = []
        polls.extend(customer.linear_scale_poll_answer.filter(completed=False))
        polls.extend(customer.paragraph_poll_answers.filter(completed=False))
        polls.extend(customer.short_answer_poll_answers.filter(completed=False))
        polls.extend(customer.multiple_choice_poll_answers.filter(completed=False))
        polls.extend(customer.checkbox_poll_answers.filter(completed=False))
        polls.sort(key=lambda poll: poll.remaining_time)
        polls = polls[page - 1 * offset: page * offset]
        serializer = PollSerializer(polls, many=True)
        return Response({
            'result': True,
            'message': 'جستجو با موفقیت انجام شد.',
            'polls': serializer.data
        })


# not completed
class CompletePoll(APIView):
    def post(self, request, Format=None):
        poll_id = request.data['poll_id']
        username = request.data['username']
        poll_type = request.data['poll_type']


class getShops(APIView):
    def post(self, request, Format=None):
        username = request.data['username']


class AddPoll(APIView):
    def post(self, request) -> Response:
        """
        TODO
        @param request:
        @return:
        """
        serializer = PollSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'result': False,
                'message': 'اضافه کردن نظرسنجی با خطا مواجه شد.'
            })
        else:
            return Response({
                'result': True,
                'message': 'اضافه کردن نظرسنجی با موفقیت انجام شد.'
            })
