# Generated by Django 3.0.2 on 2020-03-10 13:38

import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('icon', models.ImageField(blank=True, null=True, upload_to='media/')),
                ('prefecture', models.CharField(choices=[(0, '道北'), (1, '道央'), (2, '道東'), (3, '道南'), (4, '青森'), (5, '岩手'), (6, '宮城'), (7, '秋田'), (8, '山形'), (9, '福島'), (10, '東京'), (11, '神奈川'), (12, '埼玉'), (13, '千葉'), (14, '茨城'), (15, '栃木'), (16, '群馬'), (17, '山梨'), (18, '新潟'), (19, '長野'), (20, '愛知'), (21, '岐阜'), (22, '静岡'), (23, '三重'), (24, '富山'), (25, '石川'), (26, '福井'), (27, '大阪'), (28, '兵庫'), (29, '京都'), (30, '滋賀'), (31, '奈良'), (32, '和歌山'), (33, '島根'), (34, '鳥取'), (35, '岡山'), (36, '広島'), (37, '山口'), (38, '徳島'), (39, '香川'), (40, '愛媛'), (41, '高知'), (42, '福岡'), (43, '佐賀'), (44, '長崎'), (45, '熊本'), (46, '大分'), (47, '宮崎'), (48, '鹿児島'), (49, '沖縄')], default=0, max_length=2)),
                ('city', models.CharField(max_length=3)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]