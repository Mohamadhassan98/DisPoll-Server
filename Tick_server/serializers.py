from rest_framework import serializers

from Tick_server.models import Customer, Discount, Poll, CustomUser


# noinspection PyMethodMayBeStatic
# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CustomUser
#         exclude = ('customer', 'salesman')
#
#     def create(self, validated_data):
#         username = validated_data.pop('username')
#         password = validated_data.pop('password')
#         CustomUser.objects.create_user(username = username, password = password, **validated_data)
#         return CustomUser.objects.get(username = username)
#
#
# class CustomerSerializer(serializers.ModelSerializer):
#     user = UserSerializer(many = False)
#
#     class Meta:
#         model = Customer
#         fields = '__all__'
#
#     def create(self, validated_data):
#         validated_data.update({'user_type': 'CU'})
#         self.user.validate(validated_data)
#         if self.user.is_valid():
#             user = self.user.save()
#             customer = Customer.objects.create(user = user)
#             return customer
#
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'

    def create(self, validated_data):
        print('validated data:')
        print(validated_data)
        username = validated_data.pop('username')
        password = validated_data.pop('password')
        validated_data.pop('groups')
        validated_data.pop('user_permissions')
        CustomUser.objects.create_user(username = username, password = password, **validated_data)
        return CustomUser.objects.get(username = username)


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'
        depth = 1

    def create(self, validated_data):
        validated_data.update({'user_type': 'CU'})
        customer = \
            {
                'user': validated_data
            }
        serializer = UserSerializer(data = customer)
        if serializer.is_valid(raise_exception = True):
            user = serializer.save()
            return Customer.objects.create(user = user)


class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = '__all__'


class PollSerializer(serializers.ModelSerializer):
    class Meta:
        model = Poll
        fields = '__all__'
