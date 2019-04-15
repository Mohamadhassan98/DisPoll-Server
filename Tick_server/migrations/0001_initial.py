# Generated by Django 2.2 on 2019-04-14 10:20

import django.contrib.auth.models
import django.contrib.auth.validators
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name = 'CheckBoxPoll',
            fields = [
                ('id',
                 models.AutoField(auto_created = True, primary_key = True, serialize = False, verbose_name = 'ID')),
                ('importance', models.IntegerField()),
                ('remaining_time', models.DateTimeField()),
                ('text', models.TextField()),
            ],
            options = {
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name = 'City',
            fields = [
                ('id',
                 models.AutoField(auto_created = True, primary_key = True, serialize = False, verbose_name = 'ID')),
                ('name', models.CharField(max_length = 50)),
            ],
        ),
        migrations.CreateModel(
            name = 'Code4Digit',
            fields = [
                ('id',
                 models.AutoField(auto_created = True, primary_key = True, serialize = False, verbose_name = 'ID')),
                ('phone_number', models.CharField(max_length = 11)),
                ('code', models.CharField(max_length = 4)),
            ],
        ),
        migrations.CreateModel(
            name = 'Discount',
            fields = [
                ('id',
                 models.AutoField(auto_created = True, primary_key = True, serialize = False, verbose_name = 'ID')),
                ('active', models.BooleanField(default = False)),
                ('code', models.CharField(max_length = 5)),
                ('description', models.TextField()),
                ('expire_date', models.DateField()),
                ('percent', models.IntegerField()),
                ('product_brand', models.CharField(max_length = 50, null = True)),
                ('product_id', models.CharField(max_length = 50, null = True)),
                ('product_name', models.CharField(max_length = 50, null = True)),
                ('product_barcode', models.ImageField(null = True, upload_to = '')),
            ],
        ),
        migrations.CreateModel(
            name = 'LinearScalePoll',
            fields = [
                ('id',
                 models.AutoField(auto_created = True, primary_key = True, serialize = False, verbose_name = 'ID')),
                ('importance', models.IntegerField()),
                ('remaining_time', models.DateTimeField()),
                ('text', models.TextField()),
                ('answer', models.IntegerField()),
                ('choices_count', models.IntegerField()),
                ('start', models.IntegerField()),
                ('step', models.IntegerField()),
            ],
            options = {
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name = 'MultipleChoicePoll',
            fields = [
                ('id',
                 models.AutoField(auto_created = True, primary_key = True, serialize = False, verbose_name = 'ID')),
                ('importance', models.IntegerField()),
                ('remaining_time', models.DateTimeField()),
                ('text', models.TextField()),
            ],
            options = {
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name = 'ParagraphPoll',
            fields = [
                ('id',
                 models.AutoField(auto_created = True, primary_key = True, serialize = False, verbose_name = 'ID')),
                ('importance', models.IntegerField()),
                ('remaining_time', models.DateTimeField()),
                ('text', models.TextField()),
                ('answer_text', models.TextField()),
            ],
            options = {
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name = 'ShopKind',
            fields = [
                ('id',
                 models.AutoField(auto_created = True, primary_key = True, serialize = False, verbose_name = 'ID')),
                ('name', models.CharField(max_length = 50)),
            ],
        ),
        migrations.CreateModel(
            name = 'ShortAnswerPoll',
            fields = [
                ('id',
                 models.AutoField(auto_created = True, primary_key = True, serialize = False, verbose_name = 'ID')),
                ('importance', models.IntegerField()),
                ('remaining_time', models.DateTimeField()),
                ('text', models.TextField()),
                ('answer_text', models.CharField(max_length = 100)),
            ],
            options = {
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name = 'Customer',
            fields = [
                ('id',
                 models.AutoField(auto_created = True, primary_key = True, serialize = False, verbose_name = 'ID')),
                ('password', models.CharField(max_length = 128, verbose_name = 'password')),
                ('last_login', models.DateTimeField(blank = True, null = True, verbose_name = 'last login')),
                ('is_superuser', models.BooleanField(default = False,
                                                     help_text = 'Designates that this user has all permissions without explicitly assigning them.',
                                                     verbose_name = 'superuser status')),
                ('username',
                 models.CharField(error_messages = { 'unique': 'A user with that username already exists.' },
                                  help_text = 'Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
                                  max_length = 150, unique = True,
                                  validators = [django.contrib.auth.validators.UnicodeUsernameValidator()],
                                  verbose_name = 'username')),
                ('first_name', models.CharField(blank = True, max_length = 30, verbose_name = 'first name')),
                ('last_name', models.CharField(blank = True, max_length = 150, verbose_name = 'last name')),
                ('email', models.EmailField(blank = True, max_length = 254, verbose_name = 'email address')),
                ('is_staff', models.BooleanField(default = False,
                                                 help_text = 'Designates whether the user can log into this admin site.',
                                                 verbose_name = 'staff status')),
                ('is_active', models.BooleanField(default = True,
                                                  help_text = 'Designates whether this user should be treated as active. Unselect this instead of deleting accounts.',
                                                  verbose_name = 'active')),
                (
                    'date_joined',
                    models.DateTimeField(default = django.utils.timezone.now, verbose_name = 'date joined')),
                ('birth_date', models.DateField(blank = True, null = True)),
                ('gender', models.CharField(blank = True, choices = [('m', 'Male'), ('f', 'Female')], max_length = 1,
                                            null = True)),
                ('location', models.CharField(blank = True, max_length = 100, null = True)),
                ('phone_number', models.CharField(max_length = 13, unique = True)),
                ('city', models.ForeignKey(blank = True, null = True, on_delete = django.db.models.deletion.CASCADE,
                                           to = 'Tick_server.City')),
                ('groups', models.ManyToManyField(blank = True,
                                                  help_text = 'The groups this user belongs to. A user will get all permissions granted to each of their groups.',
                                                  related_name = 'user_set', related_query_name = 'user',
                                                  to = 'auth.Group', verbose_name = 'groups')),
                ('user_permissions',
                 models.ManyToManyField(blank = True, help_text = 'Specific permissions for this user.',
                                        related_name = 'user_set', related_query_name = 'user', to = 'auth.Permission',
                                        verbose_name = 'user permissions')),
            ],
            options = {
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers = [
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name = 'Shop',
            fields = [
                ('id',
                 models.AutoField(auto_created = True, primary_key = True, serialize = False, verbose_name = 'ID')),
                ('address', models.TextField()),
                ('business_license', models.ImageField(upload_to = '')),
                ('location', models.CharField(max_length = 50)),
                ('name', models.CharField(max_length = 50)),
                ('picture', models.ImageField(upload_to = '')),
                ('shop_kind', models.ManyToManyField(related_name = 'shop', to = 'Tick_server.ShopKind')),
            ],
        ),
        migrations.CreateModel(
            name = 'MultipleChoiceOption',
            fields = [
                ('id',
                 models.AutoField(auto_created = True, primary_key = True, serialize = False, verbose_name = 'ID')),
                ('answer_text', models.CharField(max_length = 100)),
                ('selected', models.BooleanField(default = False)),
                ('poll', models.ForeignKey(on_delete = django.db.models.deletion.CASCADE,
                                           to = 'Tick_server.MultipleChoicePoll')),
            ],
        ),
        migrations.CreateModel(
            name = 'CheckBoxOption',
            fields = [
                ('id',
                 models.AutoField(auto_created = True, primary_key = True, serialize = False, verbose_name = 'ID')),
                ('answer_text', models.CharField(max_length = 100)),
                ('selected', models.BooleanField(default = False)),
                ('poll',
                 models.ForeignKey(on_delete = django.db.models.deletion.CASCADE, to = 'Tick_server.CheckBoxPoll')),
            ],
        ),
        migrations.CreateModel(
            name = 'Branch',
            fields = [
                ('id',
                 models.AutoField(auto_created = True, primary_key = True, serialize = False, verbose_name = 'ID')),
                ('name', models.CharField(max_length = 50)),
                ('shop', models.ForeignKey(on_delete = django.db.models.deletion.CASCADE, to = 'Tick_server.Shop')),
            ],
        ),
    ]
