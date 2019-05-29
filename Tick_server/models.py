from django.contrib.auth.models import AbstractUser, Permission
from django.db import models
from django.utils import timezone


class City(models.Model):
    name = models.CharField(max_length=50)


class CustomUser(AbstractUser):
    TYPES = (
        ('SU', 'Super User'),
        ('CU', 'Customer'),
        ('SM', 'Salesman')
    )
    user_type = models.CharField(max_length=2, choices=TYPES)
    birth_date = models.DateField(null=True, blank=True)
    GENDER = (
        ('m', 'Male'),
        ('f', 'Female')
    )
    gender = models.CharField(max_length=1, choices=GENDER, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=13, unique=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True, blank=True)  # Not Null


# noinspection PyUnusedLocal
def upload_to_path(instance, filename):
    return 'Salesman/' + str(instance.user.email) + '.jpg'


class Salesman(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    avatar = models.ImageField(null = True, upload_to=upload_to_path)

    def check_password(self, raw_password):
        return self.user.check_password(raw_password)


class ShopKind(models.Model):
    name = models.CharField(max_length=50)


class Shop(models.Model):
    salesman = models.ForeignKey(Salesman, on_delete=models.CASCADE, null=True)
    address = models.TextField()
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True)
    business_license = models.ImageField(null=True, blank=True)
    location = models.CharField(max_length=50, blank=True, null=True)
    # phone_number = models.CharField(max_length = 11)
    name = models.CharField(max_length=50)
    shop_kind = models.ForeignKey(ShopKind, on_delete=models.CASCADE, null=True)  # NOT NULL
    picture = models.ImageField(blank=True, null=True)


class Poll(models.Model):
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
    importance = models.IntegerField(choices=IMPORTANCE)
    remaining_time = models.IntegerField()
    text = models.TextField()
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class ParagraphPoll(Poll):
    pass


class LinearScalePoll(Poll):
    choices_count = models.IntegerField()
    start = models.IntegerField()
    step = models.IntegerField()


class MultipleChoicePoll(Poll):
    pass


class MultipleChoiceOption(models.Model):
    answer_text = models.CharField(max_length=100)
    poll = models.ForeignKey(MultipleChoicePoll, on_delete=models.CASCADE)


class CheckBoxPoll(Poll):
    pass


class CheckBoxOption(models.Model):
    answer_text = models.CharField(max_length=100)
    poll = models.ForeignKey(CheckBoxPoll, on_delete=models.CASCADE)


class ShortAnswerPoll(Poll):
    pass


class Customer(models.Model):
    user = models.OneToOneField(CustomUser, related_name='customer', on_delete=models.CASCADE)
    linear_scale_poll_answers = models.ManyToManyField(LinearScalePoll, through='LinearScalePollAnswer')
    paragraph_poll_answers = models.ManyToManyField(ParagraphPoll, through='ParagraphPollAnswer')
    checkbox_poll_answers = models.ManyToManyField(CheckBoxOption, through='CheckBoxPollAnswer')
    short_answer_poll_answers = models.ManyToManyField(ShortAnswerPoll, through='ShortAnswerPollAnswer')
    multiple_choice_poll_answers = models.ManyToManyField(MultipleChoiceOption, through='MultipleChoiceAnswer')

    def check_password(self, raw_password):
        return self.user.check_password(raw_password)


class PollAnswer(models.Model):
    completed = models.BooleanField(default=False)

    class Meta:
        abstract = True


class ShortAnswerPollAnswer(PollAnswer):
    answer_text = models.CharField(max_length=100)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='short_answer_poll_answer')
    poll = models.ForeignKey(ShortAnswerPoll, on_delete=models.CASCADE, related_name='short_answer_poll_answer')


class CheckBoxPollAnswer(PollAnswer):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='checkbox_poll_answer')
    option = models.ForeignKey(CheckBoxOption, on_delete=models.CASCADE, related_name='checkbox_poll_answer')


class ParagraphPollAnswer(PollAnswer):
    answer_text = models.TextField()
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='paragraph_poll_answer')
    poll = models.ForeignKey(ParagraphPoll, on_delete=models.CASCADE, related_name='paragraph_poll_answer')


class LinearScalePollAnswer(PollAnswer):
    answer = models.IntegerField()
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='linear_scale_poll_answer')
    poll = models.ForeignKey(LinearScalePoll, on_delete=models.CASCADE, related_name='linear_scale_poll_answer')


class MultipleChoiceAnswer(PollAnswer):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='multiple_choice_answer')
    option = models.ForeignKey(MultipleChoiceOption, on_delete=models.CASCADE,
                               related_name='multiple_choice_answer')


class Code4Digit(models.Model):
    phone_number = models.CharField(max_length=11)
    code = models.CharField(max_length=4)


class Branch(models.Model):
    name = models.CharField(max_length=50)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)


class CandidateProduct(models.Model):
    description = models.TextField(blank=True)
    percent = models.IntegerField(default=5)
    count = models.IntegerField(default=5)
    product_brand = models.CharField(max_length=50, null=True)
    product_id = models.CharField(max_length=50, null=True)
    product_name = models.CharField(max_length=50, null=True)
    product_barcode = models.ImageField(null=True)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='discount')
    expire_date = models.IntegerField(default=5)


class Discount(models.Model):
    active = models.BooleanField(default=False)
    code = models.CharField(max_length=5, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='discount', null=True)
    expire_date = models.DateField(default=timezone.now)
    candidate_product = models.ForeignKey(CandidateProduct, on_delete=models.CASCADE, related_name='discount')


class Code4DigitSalesman(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=4)
    password = models.CharField(max_length=50)
