from rest_framework.authtoken.models import Token

from Tick_server.models import ShopKind, City, CustomUser

City.objects.create(name = 'ÇÕİåÇä')
City.objects.create(name = 'ÊåÑÇä')
City.objects.create(name = 'ãÔåÏ')
City.objects.create(name = 'ÔíÑÇÒ')
City.objects.create(name = 'íÒÏ')
ShopKind.objects.create(name = 'ãæÇÏ ÛĞÇíí')
ShopKind.objects.create(name = 'æÔÇ˜')
ShopKind.objects.create(name = 'ÂÑÇíÔí ÈåÏÇÔÊí')
ShopKind.objects.create(name = 'áæÇÒãÇáÊÍÑíÑ')
ShopKind.objects.create(name = 'åÊá')
user = CustomUser.objects.create_superuser(username = 'admin', email = 'emohamadhassan@gmail.com', password = 'admin')
Token.objects.create(user = user, key = 'd225d74e7447c5dc66e2845fdd23d0b02be3ba4f')
