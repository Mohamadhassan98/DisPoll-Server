from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class City(models.Model):
    name = models.CharField(max_length = 50)


class Customer(AbstractUser):
    birth_date = models.DateField(null = True, blank = True)
    GENDER = (
        ('m', 'Male'),
        ('f', 'Female')
    )
    gender = models.CharField(max_length = 1, choices = GENDER, null = True, blank = True)
    location = models.CharField(max_length = 100, null = True, blank = True)
    phone_number = models.CharField(max_length = 13, unique = True)
    city = models.ForeignKey(City, on_delete = models.CASCADE, null = True, blank = True)
    linear_scale_poll_answers = models.ManyToManyField(LinearScalePoll, through = LinearScalePollAnswer)


class Code4Digit(models.Model):
    phone_number = models.CharField(max_length = 11)
    code = models.CharField(max_length = 4)


class Salesman(Customer):
    avatar = models.ImageField()


class ShopKind(models.Model):
    name = models.CharField(max_length = 50)


class Shop(models.Model):
    address = models.TextField(blank = True)
    business_license = models.ImageField(blank = True)
    location = models.CharField(max_length = 50)
    name = models.CharField(max_length = 50)
    shop_kind = models.ManyToManyField(ShopKind, related_name = 'shop')
    picture = models.ImageField(blank = True)


class Branch(models.Model):
    name = models.CharField(max_length = 50)
    shop = models.ForeignKey(Shop, on_delete = models.CASCADE)


class Discount(models.Model):
    active = models.BooleanField(default = False)
    code = models.CharField(max_length = 5)
    description = models.TextField(blank = True)
    expire_date = models.DateField(default = timezone.now())
    percent = models.IntegerField(default = 5)
    product_brand = models.CharField(max_length = 50, null = True)
    product_id = models.CharField(max_length = 50, null = True)
    product_name = models.CharField(max_length = 50, null = True)
    product_barcode = models.ImageField(null = True)
    customer = models.ForeignKey(Customer, on_delete = models.CASCADE, related_name = 'discount')
    shop = models.ForeignKey(Shop, on_delete = models.CASCADE, related_name = 'discount')


class Poll(models.Model):
    importance = models.IntegerField()
    remaining_time = models.DateTimeField()
    text = models.TextField()

    class Meta:
        abstract = True


class LinearScalePoll(Poll):
    choices_count = models.IntegerField()
    start = models.IntegerField()
    step = models.IntegerField()


class LinearScalePollAnswer(models.Model):
    answer = models.IntegerField()
    customer = models.ForeignKey(Customer, on_delete = models.CASCADE, related_name = 'answer')
    poll = models.ForeignKey(LinearScalePoll, on_delete = models.CASCADE, related_name = 'answer')


class ParagraphPoll(Poll):
    answer_text = models.TextField()


class CheckBoxPoll(Poll):
    pass


class CheckBoxOption(models.Model):
    answer_text = models.CharField(max_length = 100)
    poll = models.ForeignKey(CheckBoxPoll, on_delete = models.CASCADE)
    selected = models.BooleanField(default = False)


class ShortAnswerPoll(Poll):
    answer_text = models.CharField(max_length = 100)


class MultipleChoicePoll(Poll):
    pass


class MultipleChoiceOption(models.Model):
    answer_text = models.CharField(max_length = 100)
    selected = models.BooleanField(default = False)
    poll = models.ForeignKey(MultipleChoicePoll, on_delete = models.CASCADE)
