# Generated by Django 3.0.2 on 2020-03-12 08:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='h_prefecture',
            field=models.CharField(choices=[(0, '道北'), (1, '道央'), (2, '道東'), (3, '道南'), (4, '青森'), (5, '岩手'), (6, '宮城'), (7, '秋田'), (8, '山形'), (9, '福島'), (10, '東京'), (11, '神奈川'), (12, '埼玉'), (13, '千葉'), (14, '茨城'), (15, '栃木'), (16, '群馬'), (17, '山梨'), (18, '新潟'), (19, '長野'), (20, '愛知'), (21, '岐阜'), (22, '静岡'), (23, '三重'), (24, '富山'), (25, '石川'), (26, '福井'), (27, '大阪'), (28, '兵庫'), (29, '京都'), (30, '滋賀'), (31, '奈良'), (32, '和歌山'), (33, '島根'), (34, '鳥取'), (35, '岡山'), (36, '広島'), (37, '山口'), (38, '徳島'), (39, '香川'), (40, '愛媛'), (41, '高知'), (42, '福岡'), (43, '佐賀'), (44, '長崎'), (45, '熊本'), (46, '大分'), (47, '宮崎'), (48, '鹿児島'), (49, '沖縄')], default=0, max_length=2),
        ),
    ]
