from Tick_server.serializers import CustomerSerializer

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
