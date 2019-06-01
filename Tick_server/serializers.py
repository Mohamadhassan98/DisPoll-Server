import os

from rest_framework import serializers

from Tick_server.models import Customer, Discount, Poll, CustomUser, Salesman, \
    Shop, CandidateProduct, ShopKind, City, CheckBoxPoll, CheckBoxOption, \
    ParagraphPoll, LinearScalePoll, MultipleChoicePoll, MultipleChoiceOption, ShortAnswerPoll


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
        validated_data.update({'is_active': True})
        CustomUser.objects.create_user(username = username, password = password, **validated_data)
        return CustomUser.objects.get(username = username)

    def update(self, instance: CustomUser, validated_data):
        print('validated data:')
        print(validated_data)
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
        # new_instance = super().update(instance, validated_data)
        # new_instance.save()
        # return new_instance


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
