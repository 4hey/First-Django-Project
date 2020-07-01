from django.test import TestCase
from accounts.models import User
#from unittest import mock
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
import os

class UserTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        User.objects.create_user(
            username='tester',
            password='test',
            prefecture=27, #大阪
            city=76, #大阪
            email='test_for_djano@gmail.com',
            icon=SimpleUploadedFile(
                name='sample.jpeg',
                content=open(os.path.join(os.environ['HOME'],'Pictures/sample.jpeg'), 'rb').read(),
                content_type='image/jpeg'
            )
        )

    def setUp(self):
        self.user = User.objects.get(id=1)


    def test_object_name_is_username(self):
        username = self.user.username
        self.assertEqual(str(self.user), username)

    def test_prefecture_label(self):
        username = self.user._meta.get_field('prefecture').verbose_name
        self.assertEqual(username, 'prefecture')

    def test_city_label(self):
        username = self.user._meta.get_field('city').verbose_name
        self.assertEqual(username, 'city')

    def test_icon_label(self):
        username = self.user._meta.get_field('icon').verbose_name
        self.assertEqual(username, 'icon')

    def test_prefecture_choices(self):
        options = [
            (0, '道北'), (1, '道央'), (2, '道東'), (3, '道南'), (4, '青森'),
            (5, '岩手'), (6, '宮城'), (7, '秋田'), (8, '山形'), (9, '福島'),
            (10, '東京'), (11, '神奈川'), (12, '埼玉'), (13, '千葉'), (14, '茨城'),
            (15, '栃木'), (16, '群馬'), (17, '山梨'), (18, '新潟'), (19, '長野'),
            (20, '愛知'), (21, '岐阜'), (22, '静岡'), (23, '三重'), (24, '富山'),
            (25, '石川'), (26, '福井'), (27, '大阪'), (28, '兵庫'), (29, '京都'),
            (30, '滋賀'), (31, '奈良'), (32, '和歌山'), (33, '島根'), (34, '鳥取'),
            (35, '岡山'), (36, '広島'), (37, '山口'), (38, '徳島'), (39, '香川'),
            (40, '愛媛'), (41, '高知'), (42, '福岡'), (43, '佐賀'), (44, '長崎'),
            (45, '熊本'), (46, '大分'), (47, '宮崎'), (48, '鹿児島'), (49, '沖縄')
        ]

        choices = self.user._meta.get_field('prefecture').choices
        self.assertEqual(choices, options)

    def test_city_choices(self):
        options = [
            (0, '稚内'), (1, '旭川'), (2, '留萌'), (3, '札幌'), (4, '岩見沢'),
            (5, '倶知安'), (6, '網走'), (7, '北見'), (8, '紋別'), (9, '根室'),
            (10, '釧路'), (11, '帯広'), (12, '室蘭'), (13, '浦河'), (14, '函館'),
            (15, '江差'), (16, '青森'), (17, 'むつ'), (18, '八戸'), (19, '盛岡'),
            (20, '宮古'), (21, '大船渡'), (22, '仙台'), (23, '白石'), (24, '秋田'),
            (25, '横手'), (26, '山形'), (27, '米沢'), (28, '酒田'), (29, '新庄'),
            (30, '福島'), (31, '小名浜'), (32, '若松'), (33, '東京'), (34, '大島'),
            (35, '八丈島'), (36, '父島'), (37, '横浜'), (38, '小田原'), (39, 'さいたま'),
            (40, '熊谷'), (41, '秩父'), (42, '千葉'), (43, '銚子'), (44, '館山'),
            (45, '水戸'), (46, '土浦'), (47, '宇都宮'), (48, '大田原'), (49, '前橋'),
            (50, 'みなかみ'), (51, '甲府'), (52, '河口湖'), (53, '新潟'), (54, '長岡'),
            (55, '高田'), (56, '相川'), (57, '長野'), (58, '松本'), (59, '飯田'),
            (60, '名古屋'), (61, '豊橋'), (62, '岐阜'), (63, '高山'), (64, '静岡'),
            (65, '網代'), (66, '三島'), (67, '浜松'), (68, '津'), (69, '尾鷲'),
            (70, '富山'), (71, '伏木'), (72, '金沢'), (73, '輪島'), (74, '福井'),
            (75, '敦賀'), (76, '大阪'), (77, '神戸'), (78, '豊岡'), (79, '京都'),
            (80, '舞鶴'), (81, '大津'), (82, '彦根'), (83, '奈良'), (84, '風屋'),
            (85, '和歌山'), (86, '潮岬'), (87, '松江'), (88, '浜田'), (89, '西郷'),
            (90, '鳥取'), (91, '米子'), (92, '岡山'), (93, '津山'), (94, '広島'),
            (95, '庄原'), (96, '下関'), (97, '山口'), (98, '柳井'), (99, '萩'),
            (100, '徳島'), (101, '日和佐'), (102, '高松'), (103, '松山'),
            (104, '新居浜'), (105, '宇和島'), (106, '高知'), (107, '室戸岬'),
            (108, '清水'), (109, '福岡'), (110, '八幡'), (111, '飯塚'), (112, '久留米'),
            (113, '佐賀'), (114, '伊万里'), (115, '長崎'), (116, '佐世保'),
            (117, '厳原'), (118, '福江'), (119, '熊本'), (120, '阿蘇乙姫'),
            (121, '牛深'), (122, '人吉'), (123, '大分'), (124, '中津'), (125, '日田'),
            (126, '佐伯'), (127, '宮崎'), (128, '延岡'), (129, '都城'), (130, '高千穂'),
            (131, '名瀬'), (132, '鹿児島'), (133, '鹿屋'), (134, '種子島'),
            (135, '那覇'), (136, '名護'), (137, '久米島'), (138, '南大東'),
            (139, '宮古島'), (140, '石垣島'), (141, '与那国島')
        ]

        choices = self.user._meta.get_field('city').choices
        self.assertEqual(choices, options)

    def test_icon_upload_to(self):
        upload_to = self.user._meta.get_field('icon').upload_to
        self.assertEqual(upload_to, 'media')

    def test_icon_blank(self):
        blank = self.user._meta.get_field('icon').blank
        self.assertEqual(blank, True)

    def test_get_absolute_url(self):
        print(self.user.get_absolute_url())
        self.assertEqual(self.user.get_absolute_url(), reverse('weatherapp:home'))
