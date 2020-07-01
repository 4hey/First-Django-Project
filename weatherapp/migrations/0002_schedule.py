# Generated by Django 3.0.2 on 2020-03-01 07:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('weatherapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
                ('detail', models.CharField(max_length=200)),
                ('start', models.CharField(choices=[(0, '0:00'), (1, '0:30'), (2, '1:00'), (3, '1:30'), (4, '2:00'), (5, '2:30'), (6, '3:00'), (7, '3:30'), (8, '4:00'), (9, '4:30'), (10, '5:00'), (11, '5:30'), (12, '6:00'), (13, '6:30'), (14, '7:00'), (15, '7:30'), (16, '8:00'), (17, '8:30'), (18, '9:00'), (19, '9:30'), (20, '10:00'), (21, '10:30'), (22, '11:00'), (23, '11:30'), (24, '12:00'), (25, '12:30'), (26, '13:00'), (27, '13:30'), (28, '14:00'), (29, '14:30'), (30, '15:00'), (31, '15:30'), (32, '16:00'), (33, '16:30'), (34, '17:00'), (35, '17:30'), (36, '18:00'), (37, '18:30'), (38, '19:00'), (39, '19:30'), (40, '20:00'), (41, '20:30'), (42, '21:00'), (43, '21:30'), (44, '22:00'), (45, '22:30'), (46, '23:00'), (47, '23:30')], default=0, max_length=2)),
                ('end', models.CharField(choices=[(0, '0:00'), (1, '0:30'), (2, '1:00'), (3, '1:30'), (4, '2:00'), (5, '2:30'), (6, '3:00'), (7, '3:30'), (8, '4:00'), (9, '4:30'), (10, '5:00'), (11, '5:30'), (12, '6:00'), (13, '6:30'), (14, '7:00'), (15, '7:30'), (16, '8:00'), (17, '8:30'), (18, '9:00'), (19, '9:30'), (20, '10:00'), (21, '10:30'), (22, '11:00'), (23, '11:30'), (24, '12:00'), (25, '12:30'), (26, '13:00'), (27, '13:30'), (28, '14:00'), (29, '14:30'), (30, '15:00'), (31, '15:30'), (32, '16:00'), (33, '16:30'), (34, '17:00'), (35, '17:30'), (36, '18:00'), (37, '18:30'), (38, '19:00'), (39, '19:30'), (40, '20:00'), (41, '20:30'), (42, '21:00'), (43, '21:30'), (44, '22:00'), (45, '22:30'), (46, '23:00'), (47, '23:30')], default=0, max_length=2)),
                ('place', models.CharField(choices=[('in', '屋内'), ('out', '屋外')], default='in', max_length=3)),
            ],
        ),
    ]
