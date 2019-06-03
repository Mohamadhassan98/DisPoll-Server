import os

from rest_framework.authtoken.models import Token

from Tick_server.models import ShopKind, City, CustomUser

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tick_project.settings')
    City.objects.create(name = 'اصفهان')
    City.objects.create(name = 'شیراز')
    City.objects.create(name = 'تهران')
    City.objects.create(name = 'یزد')
    City.objects.create(name = 'مشهد')
    ShopKind.objects.create(name = 'مواد غذایی')
    ShopKind.objects.create(name = 'پوشاک')
    ShopKind.objects.create(name = 'آرایشی بهداشتی')
    ShopKind.objects.create(name = 'لوازم التحریر')
    ShopKind.objects.create(name = 'هتل')
    user = CustomUser.objects.create_superuser(username = 'admin', email = 'emohamadhassan@gmail.com',
                                               password = 'admin')
    Token.objects.create(user = user, key = 'd225d74e7447c5dc66e2845fdd23d0b02be3ba4f')
