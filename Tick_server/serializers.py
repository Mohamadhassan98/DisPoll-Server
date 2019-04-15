from rest_framework import serializers

from Tick_server.models import Customer, Discount


# noinspection PyMethodMayBeStatic
class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

    def create(self, validated_data):
        username = validated_data.pop('username')
        password = validated_data.pop('password')
        Customer.objects.create_user(username = username, password = password, **validated_data)
        return Customer.objects.get(username = username)


class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = '__all__'
