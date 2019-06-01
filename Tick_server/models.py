import datetime
import time

from django.contrib.auth.models import AbstractUser, Permission
from django.db import models


class City(models.Model):
    name = models.CharField(max_length = 50)


class CustomUser(AbstractUser):
    TYPES = (
        ('SU', 'Super User'),
        ('CU', 'Customer'),
        ('SM', 'Salesman')
    )
    user_type = models.CharField(max_length = 2, choices = TYPES)
    birth_date = models.DateField(null = True, blank = True)
    GENDER = (
        ('m', 'Male'),
        ('f', 'Female')
    )
    gender = models.CharField(max_length = 1, choices = GENDER, null = True, blank = True)
    location = models.CharField(max_length = 100, null = True, blank = True)
    phone_number = models.CharField(max_length = 13, unique = True)
    city = models.ForeignKey(City, on_delete = models.CASCADE, related_name = 'users', null = True, blank = True)


# noinspection PyUnusedLocal
def upload_salesman_to_path(instance, filename):
    return 'Salesman/' + str(instance.user.username) + '.jpg'


class Salesman(models.Model):
    user = models.OneToOneField(CustomUser, on_delete = models.CASCADE, related_name = 'salesman')
    avatar = models.ImageField(upload_to = upload_salesman_to_path,
                               default = 'Salesman/antihippopotomonstrosesquippedaliophobiaantihippopotomonstrosesquippedaliophobiaantihippopotomonstrosesquippedaliophobiaantihippopotomonstrosesquippedaliophobia.jpg')

    def check_password(self, raw_password):
        return self.user.check_password(raw_password)


class ShopKind(models.Model):
    name = models.CharField(max_length = 50)


# noinspection PyUnusedLocal
def upload_shop_to_path(instance, filename):
    return 'Shop/shop_' + str(time.time_ns()) + '.jpg'


# noinspection PyUnusedLocal
def upload_license_to_path(instance, filename):
    return 'Business-License/license_' + str(time.time_ns()) + '.jpg'


class Shop(models.Model):
    salesman = models.ForeignKey(Salesman, on_delete = models.CASCADE, related_name = 'shops')
    address = models.TextField()
    city = models.ForeignKey(City, on_delete = models.CASCADE, related_name = 'shops', null = True)
    business_license = models.ImageField(upload_to = upload_license_to_path)
    location = models.CharField(max_length = 50, blank = True, null = True)
    phone_number = models.CharField(max_length = 11)
    name = models.CharField(max_length = 50)
    shop_kind = models.ForeignKey(ShopKind, on_delete = models.CASCADE, related_name = 'shops')
    picture = models.ImageField(upload_to = upload_shop_to_path, default = 'Shop/default.jpg')


class Poll(models.Model):
    POLL_TYPE = (
        ('LinearScalePoll', 'LinearScalePoll'),
        ('CheckBoxPoll', 'CheckBoxPoll'),
        ('MultipleChoicePoll', 'MultipleChoicePoll'),
        ('ShortAnswerPoll', 'ShortAnswerPoll'),
        ('ParagraphPoll', 'ParagraphPoll')
    )
    IMPORTANCE = (
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
        (6, 6),
        (7, 7),
        (8, 8),
        (9, 9),
        (10, 10)
    )
    type_poll = models.CharField(choices = POLL_TYPE, max_length = 20)
    importance = models.IntegerField(choices = IMPORTANCE)
    expire_date = models.DateField()
    text = models.TextField()
    shop = models.ForeignKey(Shop, on_delete = models.CASCADE, related_name = 'polls')


class ParagraphPoll(models.Model):
    poll = models.OneToOneField(Poll, related_name = 'paragraph_poll', on_delete = models.CASCADE)


class LinearScalePoll(models.Model):
    choices_count = models.IntegerField()
    start = models.IntegerField()
    step = models.IntegerField()
    poll = models.OneToOneField(Poll, related_name = 'linear_scale_poll', on_delete = models.CASCADE)


class MultipleChoicePoll(models.Model):
    poll = models.OneToOneField(Poll, related_name = 'multiple_choice_poll', on_delete = models.CASCADE)


class CheckBoxPoll(models.Model):
    poll = models.OneToOneField(Poll, related_name = 'check_box_poll', on_delete = models.CASCADE)


class ShortAnswerPoll(models.Model):
    poll = models.OneToOneField(Poll, related_name = 'short_answer_poll', on_delete = models.CASCADE)


class Customer(models.Model):
    user = models.OneToOneField(CustomUser, related_name = 'customer', on_delete = models.CASCADE)
    linear_scale_polls = models.ManyToManyField(LinearScalePoll, through = 'LinearScalePollAnswer',
                                                related_name = 'customers')
    paragraph_polls = models.ManyToManyField(ParagraphPoll, through = 'ParagraphPollAnswer', related_name = 'customers')
    check_box_polls = models.ManyToManyField(CheckBoxPoll, through = 'CheckBoxPollAnswer', related_name = 'customers')
    short_answer_polls = models.ManyToManyField(ShortAnswerPoll, through = 'ShortAnswerPollAnswer',
                                                related_name = 'customers')
    multiple_choice_polls = models.ManyToManyField(MultipleChoicePoll, through = 'MultipleChoiceAnswer',
                                                   related_name = 'customers')

    def check_password(self, raw_password):
        return self.user.check_password(raw_password)


class PollAnswer(models.Model):
    completed = models.BooleanField(default = False)
    POLL_TYPE = (
        ('LinearScalePoll', 'LinearScalePoll'),
        ('CheckBoxPoll', 'CheckBoxPoll'),
        ('MultipleChoicePoll', 'MultipleChoicePoll'),
        ('ShortAnswerPoll', 'ShortAnswerPoll'),
        ('ParagraphPoll', 'ParagraphPoll')
    )
    type_poll = models.CharField(max_length = 20, choices = POLL_TYPE)


class ShortAnswerPollAnswer(models.Model):
    poll_answer = models.OneToOneField(PollAnswer, on_delete = models.CASCADE,
                                       related_name = 'short_answer_poll_answer')
    answer_text = models.CharField(max_length = 100, null = True)
    customer = models.ForeignKey(Customer, on_delete = models.CASCADE, related_name = 'short_answer_poll_answers')
    poll = models.ForeignKey(ShortAnswerPoll, on_delete = models.CASCADE, related_name = 'short_answer_poll_answers')


class CheckBoxOption(models.Model):
    index = models.IntegerField()
    answer_text = models.CharField(max_length = 100)
    poll = models.ForeignKey(CheckBoxPoll, on_delete = models.CASCADE, related_name = 'options')


class CheckBoxPollAnswer(models.Model):
    poll_answer = models.OneToOneField(PollAnswer, on_delete = models.CASCADE, related_name = 'check_box_poll_answer')
    customer = models.ForeignKey(Customer, on_delete = models.CASCADE, related_name = 'check_box_poll_answers')
    check_box_poll = models.ForeignKey(CheckBoxPoll, on_delete = models.CASCADE,
                                       related_name = 'check_box_poll_answers')
    options = models.ManyToManyField(CheckBoxOption, related_name = 'answers')


class ParagraphPollAnswer(models.Model):
    poll_answer = models.OneToOneField(PollAnswer, on_delete = models.CASCADE, related_name = 'paragraph_poll_answer')
    answer_text = models.TextField(null = True)
    customer = models.ForeignKey(Customer, on_delete = models.CASCADE, related_name = 'paragraph_poll_answers')
    poll = models.ForeignKey(ParagraphPoll, on_delete = models.CASCADE, related_name = 'paragraph_poll_answers')


class LinearScalePollAnswer(models.Model):
    poll_answer = models.OneToOneField(PollAnswer, on_delete = models.CASCADE,
                                       related_name = 'linear_scale_poll_answer')
    answer = models.IntegerField(null = True)
    customer = models.ForeignKey(Customer, on_delete = models.CASCADE, related_name = 'linear_scale_poll_answers')
    poll = models.ForeignKey(LinearScalePoll, on_delete = models.CASCADE, related_name = 'linear_scale_poll_answers')


class MultipleChoiceOption(models.Model):
    index = models.IntegerField()
    answer_text = models.CharField(max_length = 100, null = True)
    poll = models.ForeignKey(MultipleChoicePoll, on_delete = models.CASCADE, related_name = 'options')


class MultipleChoiceAnswer(models.Model):
    poll_answer = models.OneToOneField(PollAnswer, on_delete = models.CASCADE,
                                       related_name = 'multiple_choice_poll_answer')
    customer = models.ForeignKey(Customer, on_delete = models.CASCADE, related_name = 'multiple_choice_answers')
    multiple_choice = models.ForeignKey(MultipleChoicePoll, on_delete = models.CASCADE,
                                        related_name = 'multiple_choice_answers')
    option = models.ForeignKey(MultipleChoiceOption, on_delete = models.CASCADE,
                               related_name = 'answers', null = True)


class Code4Digit(models.Model):
    phone_number = models.CharField(max_length = 11)
    code = models.CharField(max_length = 4)


class Branch(models.Model):
    name = models.CharField(max_length = 50)
    shop = models.ForeignKey(Shop, on_delete = models.CASCADE, related_name = 'branches')


class CandidateProduct(models.Model):
    description = models.TextField(blank = True)
    percent = models.IntegerField(default = 5)
    count = models.IntegerField(default = 5)
    product_brand = models.CharField(max_length = 50, null = True)
    product_id = models.CharField(max_length = 50, null = True)
    product_name = models.CharField(max_length = 50, null = True)
    product_barcode = models.ImageField(null = True)
    shop = models.ForeignKey(Shop, on_delete = models.CASCADE, related_name = 'discounts')
    expire_date = models.DateField()
    days = models.IntegerField(default = 5)


class Discount(models.Model):
    active = models.BooleanField(default = True)
    code = models.CharField(max_length = 5, unique = True)
    customer = models.ForeignKey(Customer, on_delete = models.CASCADE, related_name = 'discounts')
    candidate_product = models.ForeignKey(CandidateProduct, on_delete = models.CASCADE, related_name = 'discounts')
    start_date = models.DateField(default = datetime.date.today)


class Code4DigitSalesman(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length = 4)
    password = models.CharField(max_length = 50)
