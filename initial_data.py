from rest_framework.authtoken.models import Token

from Tick_server.models import ShopKind, City, CustomUser

City.objects.create(name = '������')
City.objects.create(name = '�����')
City.objects.create(name = '����')
City.objects.create(name = '�����')
City.objects.create(name = '���')
ShopKind.objects.create(name = '���� �����')
ShopKind.objects.create(name = '���ǘ')
ShopKind.objects.create(name = '������ �������')
ShopKind.objects.create(name = '������������')
ShopKind.objects.create(name = '���')
user = CustomUser.objects.create_superuser(username = 'admin', email = 'emohamadhassan@gmail.com', password = 'admin')
Token.objects.create(user = user, key = 'd225d74e7447c5dc66e2845fdd23d0b02be3ba4f')
