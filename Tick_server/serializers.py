from rest_framework import serializers

from Tick_server.models import Customer, Discount, Poll, CustomUser, Salesman, Shop, CandidateProduct, ShopKind, City


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


class SalesmanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Salesman
        fields = '__all__'


class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = '__all__'


class PollSerializer(serializers.ModelSerializer):
    class Meta:
        model = Poll
        fields = '__all__'


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = '__all__'


class CandidateProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateProduct
        fields = '__all__'


class ShopKindSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopKind
        fields = '__all__'


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = '__all__'
