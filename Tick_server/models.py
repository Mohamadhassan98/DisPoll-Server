from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class ShopKind(models.Model):
    name = models.CharField(max_length = 50)


class Shop(models.Model):
    address = models.TextField(blank = True)
    business_license = models.ImageField(blank = True)
    location = models.CharField(max_length = 50)
    name = models.CharField(max_length = 50)
    shop_kind = models.ManyToManyField(ShopKind, related_name = 'shop')
    picture = models.ImageField(blank = True)


class Poll(models.Model):
    importance = models.IntegerField()
    remaining_time = models.DateTimeField()
    text = models.TextField()
    shop = models.ForeignKey(Shop, on_delete = models.CASCADE)

    class Meta:
        abstract = True


class City(models.Model):
    name = models.CharField(max_length = 50)


class ParagraphPoll(Poll):
    pass


class LinearScalePoll(Poll):
    choices_count = models.IntegerField()
    start = models.IntegerField()
    step = models.IntegerField()


class MultipleChoicePoll(Poll):
    pass


class MultipleChoiceOption(models.Model):
    answer_text = models.CharField(max_length = 100)
    poll = models.ForeignKey(MultipleChoicePoll, on_delete = models.CASCADE)


class CheckBoxPoll(Poll):
    pass


class CheckBoxOption(models.Model):
    answer_text = models.CharField(max_length = 100)
    poll = models.ForeignKey(CheckBoxPoll, on_delete = models.CASCADE)


class ShortAnswerPoll(Poll):
    pass


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
    linear_scale_poll_answers = models.ManyToManyField(LinearScalePoll, through = 'LinearScalePollAnswer')
    paragraph_poll_answers = models.ManyToManyField(ParagraphPoll, through = 'ParagraphPollAnswer')
    checkbox_poll_answers = models.ManyToManyField(CheckBoxOption, through = 'CheckBoxPollAnswer')
    short_answer_poll_answers = models.ManyToManyField(ShortAnswerPoll, through = 'ShortAnswerPollAnswer')
    multiple_choice_poll_answers = models.ManyToManyField(MultipleChoiceOption, through = 'MultipleChoiceAnswer')


class PollAnswer(models.Model):
    completed = models.BooleanField(default = False)

    class Meta:
        abstract = True


class ShortAnswerPollAnswer(PollAnswer):
    answer_text = models.CharField(max_length = 100)
    customer = models.ForeignKey(Customer, on_delete = models.CASCADE, related_name = 'short_answer_poll_answer')
    poll = models.ForeignKey(ShortAnswerPoll, on_delete = models.CASCADE, related_name = 'short_answer_poll_answer')


class CheckBoxPollAnswer(PollAnswer):
    customer = models.ForeignKey(Customer, on_delete = models.CASCADE, related_name = 'checkbox_poll_answer')
    option = models.ForeignKey(CheckBoxOption, on_delete = models.CASCADE, related_name = 'checkbox_poll_answer')


class ParagraphPollAnswer(PollAnswer):
    answer_text = models.TextField()
    customer = models.ForeignKey(Customer, on_delete = models.CASCADE, related_name = 'paragraph_poll_answer')
    poll = models.ForeignKey(ParagraphPoll, on_delete = models.CASCADE, related_name = 'paragraph_poll_answer')


class LinearScalePollAnswer(PollAnswer):
    answer = models.IntegerField()
    customer = models.ForeignKey(Customer, on_delete = models.CASCADE, related_name = 'linear_scale_poll_answer')
    poll = models.ForeignKey(LinearScalePoll, on_delete = models.CASCADE, related_name = 'linear_scale_poll_answer')


class MultipleChoiceAnswer(PollAnswer):
    customer = models.ForeignKey(Customer, on_delete = models.CASCADE, related_name = 'multiple_choice_answer')
    option = models.ForeignKey(MultipleChoiceOption, on_delete = models.CASCADE,
                               related_name = 'multiple_choice_answer')


class Code4Digit(models.Model):
    phone_number = models.CharField(max_length = 11)
    code = models.CharField(max_length = 4)


class Salesman(Customer):
    avatar = models.ImageField()


class Branch(models.Model):
    name = models.CharField(max_length = 50)
    shop = models.ForeignKey(Shop, on_delete = models.CASCADE)


class Discount(models.Model):
    active = models.BooleanField(default = False)
    code = models.CharField(max_length = 5)
    description = models.TextField(blank = True)
    expire_date = models.DateField(default = timezone.now)
    percent = models.IntegerField(default = 5)
    product_brand = models.CharField(max_length = 50, null = True)
    product_id = models.CharField(max_length = 50, null = True)
    product_name = models.CharField(max_length = 50, null = True)
    product_barcode = models.ImageField(null = True)
    customer = models.ForeignKey(Customer, on_delete = models.CASCADE, related_name = 'discount')
    shop = models.ForeignKey(Shop, on_delete = models.CASCADE, related_name = 'discount')
