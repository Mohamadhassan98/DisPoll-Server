from Tick_server.serializers import CustomerSerializer, UserSerializer

customer = \
    {
        'phone_number': '09131674340'
    }

serializer = CustomerSerializer(data = customer)
serializer.is_valid()
serializer.save()

if __name__ == '__main__':
    class B:
        pass


    class A:
        def __init__(self):
            self.a = 2
            self.b = B()


    import json

    a = A()
    print(json.dumps(a))

c1 = \
    {
        'phone_number': '09130172688',
        'username': 'mohamadhassan',
        'password': '1234',
        'user_type': 'CU',
        'errors': '1234444'
    }

ser = UserSerializer(data = c1)
ser.is_valid()

c2 = \
    {
        'user':
            {
                'phone_number': '09130172688',
                'username': 'mohamadhassan',
                'password': '1234',
                'user_type': 'CU'
            }
    }
ser = CustomerSerializer(data = {})
ser.is_valid()

c3 = \
    {
        'phone_number': '09130172688',
        'username': 'mohamadhassan',
        'password': '1234'
    }
ser = CustomerSerializer(c3)
ser.is_valid()
