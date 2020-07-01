from django.test import TestCase
from django.test.client import Client
from django.urls import reverse
from accounts.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from weatherapp.models import WeatherForecast

import os


class SignUpViewTest(TestCase):

    def setUp(self):
        client = Client()

        for i in range(8):
            WeatherForecast.objects.create(
                prefecture='東京',
                city='東京',
                how_many_days_latter=i,
                weather='東京の天気'+ str(i)
            )
        for i in range(8):
            WeatherForecast.objects.create(
                prefecture='大阪',
                city='大阪',
                how_many_days_latter=i,
                weather='大阪の天気'+ str(i)
            )
        self.user1 = User.objects.create_user(
            username='tester',
            password='test',
            prefecture=27, #大阪
            city=76 #大阪
        )

    def test_view_url_exists_an_desired_location(self):
        response = self.client.get('/accounts/signup/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/signup.html')
        self.assertEqual(response.context['initial'], True)
        self.assertContains(response, 'prefecture')

    def test_view_name_exists_an_desired_location(self):
        response = self.client.get(reverse('accounts:signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/signup.html')

    def test_view_name_exists_an_desired_location2(self):
        response = self.client.post(reverse('accounts:signup'), {'button': 'choice', 'prefecture':23})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/signup.html')
        self.assertContains(response, 'prefecture')
        self.assertContains(response, 'city')
        self.assertContains(response, 'username')
        self.assertContains(response, 'email')
        self.assertContains(response, 'icon')
        self.assertEqual(response.context['form'].initial['prefecture'], '23')

    def test_view_name_exists_an_desired_location3(self):
        with open(os.path.join(os.environ['HOME'],'Pictures/sample.jpeg'), 'rb') as img:
            response = self.client.post(reverse('accounts:signup'), {
                'button': 'register',
                'prefecture':23,
                'city':68,
                'username':'tester2',
                'email':'tester@gmail.com',
                'icon':img,
                'password1':'testpassword',
                'password2':'testpassword',
            })
            self.assertEqual(response.status_code, 302)
            self.assertRedirects(response, reverse('weatherapp:home'))
            #DBに保存できているかの確認
            self.assertEqual(User.objects.get(id=2).username, 'tester2')

    def test_view_name_exists_an_desired_location4(self):
        with open(os.path.join(os.environ['HOME'],'Pictures/sample.jpeg'), 'rb') as img:
            response = self.client.post(reverse('accounts:signup'), {
                'button': 'register',
                'prefecture':23,
                'city':68,
                'username':'tester2',
                'email':'tester@gmail.com',
                'icon':img,
                'password1':'testpassword',
                'password2':'testpassword',
            }, follow=True)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.redirect_chain[0][0], '/weatherapp/')
            messages = list(response.context['messages'])
            self.assertEqual(str(messages[0]), '登録完了です')
            self.assertEqual(User.objects.get(id=2).username, 'tester2')

    def test_view_name_exists_an_desired_location5(self):
        self.client.login(username='tester', password='test')
        response = self.client.get(reverse('accounts:signup'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('weatherapp:home'))


class UserUpdateViewTest(TestCase):
    def setUp(self):
        client = Client()

        self.user1 = User.objects.create_user(
            username='tester',
            password='test',
            email = 'test@gmail.com',
            prefecture=27, #大阪
            city=76 #大阪
        )
        self.user2 = User.objects.create_user(
            username='tester2',
            password='test2',
            email = 'test2@gmail.com',
            prefecture=23, #三重
            city=68 #津
        )

    def test_view_url_exists_an_desired_location(self):
        self.client.login(username='tester', password='test')
        response = self.client.get('/accounts/1/update/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/user_update.html')

    def test_not_logged_in_user_403(self):
        response = self.client.get('/accounts/1/update/')
        self.assertEqual(response.status_code, 403)

    def test_logged_in_user_can_not_update_other(self):
        self.client.login(username='tester', password='test')
        response = self.client.get('/accounts/2/update/')
        self.assertEqual(response.status_code, 403)

    def test_view_name_exists_an_desired_location(self):
        self.client.login(username='tester', password='test')
        response = self.client.get(reverse('accounts:update', kwargs={'pk':self.user1.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/user_update.html')
        self.assertContains(response, 'username')
        self.assertContains(response, 'email')
        self.assertContains(response, 'icon')
        self.assertEqual(response.context['form'].initial['username'], 'tester')
        self.assertEqual(response.context['form'].initial['email'], 'test@gmail.com')
        self.assertEqual(str(response.context['form'].initial['icon']), '')

    def test_view_name_exists_an_desired_location2(self):
        self.client.login(username='tester', password='test')
        with open(os.path.join(os.environ['HOME'], 'Pictures/sample.jpeg'), 'rb') as img:
            response = self.client.post(reverse('accounts:update', kwargs={'pk':self.user1.id}),{
                'username':'update_tester',
                'email':'update@gmail.com',
                'icon': img
            })
            self.assertEqual(response.status_code, 302)
            self.assertRedirects(response, reverse('accounts:detail', kwargs={'pk':self.user1.id}))
            self.assertEqual(User.objects.get(id=1).username, 'update_tester')

    def test_view_name_exists_an_desired_location3(self):
        self.client.login(username='tester', password='test')
        with open(os.path.join(os.environ['HOME'], 'Pictures/sample.jpeg'), 'rb') as img:
            response = self.client.post(reverse('accounts:update', kwargs={'pk':self.user1.id}),{
                'username':'update_tester',
                'email':'update@gmail.com',
                'icon': img
            }, follow=True)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.redirect_chain[0][0], '/accounts/1/detail/')
            messages = list(response.context['messages'])
            self.assertEqual(str(messages[0]), 'ユーザー情報を更新しました')
            self.assertEqual(User.objects.get(id=1).username, 'update_tester')


class UserDetailViewTest(TestCase):
    def setUp(self):
        client = Client()

        self.user1 = User.objects.create_user(
            username='tester',
            password='test',
            email = 'test@gmail.com',
            prefecture=27, #大阪
            city=76 #大阪
        )
        self.user2 = User.objects.create_user(
            username='tester2',
            password='test2',
            email = 'test2@gmail.com',
            prefecture=23, #三重
            city=68 #津
        )

    def test_view_url_exists_an_desired_location(self):
        self.client.login(username='tester', password='test')
        response = self.client.get('/accounts/1/detail/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/user_detail.html')

    def test_not_logged_in_user_403(self):
        response = self.client.get('/accounts/1/detail/')
        self.assertEqual(response.status_code, 403)

    def test_logged_in_user_can_not_detail_other(self):
        self.client.login(username='tester', password='test')
        response = self.client.get('/accounts/2/detail/')
        self.assertEqual(response.status_code, 403)

    def test_view_name_exists_an_desired_location(self):
        self.client.login(username='tester', password='test')
        response = self.client.get(reverse('accounts:detail', kwargs={'pk':self.user1.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/user_detail.html')
        self.assertEqual(response.context['object'], self.user1)


class SignOutViewTest(TestCase):
    def setUp(self):
        client = Client()

        for i in range(8):
            WeatherForecast.objects.create(
                prefecture='東京',
                city='東京',
                how_many_days_latter=i,
                weather='東京の天気'+ str(i)
            )

        self.user1 = User.objects.create_user(
            username='tester',
            password='test',
            email = 'test@gmail.com',
            prefecture=27, #大阪
            city=76 #大阪
        )
        self.user2 = User.objects.create_user(
            username='tester2',
            password='test2',
            email = 'test2@gmail.com',
            prefecture=23, #三重
            city=68 #津
        )

    def test_view_url_exists_an_desired_location(self):
        self.client.login(username='tester', password='test')
        response = self.client.get('/accounts/1/signout/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/signout.html')

    def test_not_logged_in_user_403(self):
        response = self.client.get('/accounts/1/signout/')
        self.assertEqual(response.status_code, 403)

    def test_logged_in_user_can_not_signout_other(self):
        self.client.login(username='tester', password='test')
        response = self.client.get('/accounts/2/signout/')
        self.assertEqual(response.status_code, 403)

    def test_view_name_exists_an_desired_location(self):
        self.client.login(username='tester', password='test')
        response = self.client.get(reverse('accounts:signout', kwargs={'pk':self.user1.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/signout.html')

    def test_view_name_exists_an_desired_location2(self):
        self.client.login(username='tester', password='test')
        response = self.client.post(reverse('accounts:signout', kwargs={'pk':self.user1.id}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('weatherapp:home'))

    def test_view_name_exists_an_desired_location3(self):
        self.client.login(username='tester', password='test')
        response = self.client.post(reverse('accounts:signout', kwargs={'pk':self.user1.id}), follow=True)
        self.assertEqual(response.redirect_chain[0][0], '/weatherapp/')
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(str(messages[0]), '退会手続きが完了しました')
        self.assertFalse(self.client.login(username='tester', password='test'))
