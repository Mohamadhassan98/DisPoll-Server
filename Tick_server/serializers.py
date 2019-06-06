import os

from rest_framework import serializers
from rest_framework.exceptions import ErrorDetail

from Tick_server.models import *


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            'username', 'email', 'password', 'user_type', 'birth_date', 'gender', 'location', 'phone_number', 'city',
            'first_name', 'last_name'
        )

    def update(self, instance: CustomUser, validated_data):
        instance.birth_date = validated_data.get('birth_date', instance.birth_date)
        instance.gender = validated_data.get('gender', instance.gender)
        instance.location = validated_data.get('location', instance.location)
        instance.city = validated_data.get('city', instance.city)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        if instance.user_type == 'CU':
            instance.email = validated_data.get('email', instance.email)
        elif instance.user_type == 'SM':
            instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
        instance.save()
        return instance


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            'username', 'email', 'password', 'user_type', 'birth_date', 'gender', 'location', 'phone_number', 'city',
            'first_name', 'last_name'
        )

    def validate(self, attrs):
        if attrs['user_type'] == 'CU':
            if CustomUser.objects.filter(phone_number = attrs['phone_number'], user_type = 'CU').count() != 0:
                raise serializers.ValidationError(
                    {'phone_number': [
                        ErrorDetail(string = 'A user with that phone_number already exists.', code = 'unique')]})
        if attrs['user_type'] == 'SM':
            if CustomUser.objects.filter(email = attrs['email'], user_type = 'SM').count() != 0:
                raise serializers.ValidationError(
                    {'email': [ErrorDetail(string = 'A user with that email already exists.', code = 'unique')]})
        return attrs

    def create(self, validated_data):
        username = validated_data.pop('username')
        password = validated_data.pop('password')
        validated_data.update({'is_active': True})
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

    def update(self, instance, validated_data):
        if os.path.isfile('new-temp/Salesman/' + instance.user.username + '.jpg') and 'avatar' in validated_data:
            os.remove('new-temp/Salesman/' + instance.user.username + '.jpg')
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.save()
        return instance


class AdvertisementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advertisement
        fields = '__all__'


class GetAdvertisementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advertisement
        fields = '__all__'
        depth = 1


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

    def update(self, instance: Shop, validated_data):
        instance.address = validated_data.get('address', instance.address)
        instance.city = validated_data.get('city', instance.city)
        instance.location = validated_data.get('location', instance.location)
        instance.name = validated_data.get('name', instance.name)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.shop_kind = validated_data.get('shop_kind', instance.shop_kind)
        if os.path.isfile('new-temp/' + str(instance.business_license)) and 'business_license' in validated_data:
            os.remove('new-temp/' + str(instance.business_license))
        instance.business_license = validated_data.get('business_license', instance.business_license)
        if os.path.isfile('new-temp/' + str(instance.picture)) and 'picture' in validated_data:
            os.remove('new-temp/' + str(instance.picture))
        instance.picture = validated_data.get('picture', instance.picture)
        instance.save()
        return instance


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


class CheckBoxPollSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckBoxPoll
        fields = '__all__'


class CheckBoxPollOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckBoxOption
        fields = '__all__'


class ParagraphPollSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParagraphPoll
        fields = '__all__'


class LinearScalePollSerializer(serializers.ModelSerializer):
    class Meta:
        model = LinearScalePoll
        fields = '__all__'


class MultipleChoicePollSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultipleChoicePoll
        fields = '__all__'


class MultipleChoiceOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultipleChoiceOption
        fields = '__all__'


class ShortAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShortAnswerPoll
        fields = '__all__'


class GetShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = '__all__'
        depth = 1


class Code4DigitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Code4Digit
        fields = '__all__'
