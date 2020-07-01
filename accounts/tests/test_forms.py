from django.test import TestCase
from accounts.forms import SignUpForm, UserUpdateForm, SignOutForm
import os
from django.core.files.uploadedfile import SimpleUploadedFile


class SignUpFormTest(TestCase):

    def test_prefecture_label(self):
        form = SignUpForm()
        self.assertTrue(form.fields['prefecture'].label == 'Prefecture')

    def test_city_label(self):
        form = SignUpForm()
        self.assertTrue(form.fields['city'].label == 'City')

    def test_icon_label(self):
        form = SignUpForm()
        self.assertTrue(form.fields['icon'].label == 'Icon')

    def test_form_is_valid(self):
        post_dict = {
            'username':'tester',
            'password1':'testpassword',
            'password2':'testpassword',
            'email':'test@gmail.com',
            'prefecture':27, #大阪
            'city':76, #大阪
        }
        files_dict = {
            'icon':SimpleUploadedFile(
                name='sample.jpeg',
                content=open(os.path.join(os.environ['HOME'],'Pictures/sample.jpeg'), 'rb').read(),
                content_type='image/jpeg'
            )
        }
        form = SignUpForm(post_dict, files_dict)
        self.assertTrue(form.is_valid())

    def test_prefecture_is_valid(self):
        prefecture = 50
        post_dict = {
            'username':'tester',
            'password1':'testpassword',
            'password2':'testpassword',
            'email':'test@gmail.com',
            'prefecture':prefecture,
            'city':76
        }
        files_dict = {
            'icon':SimpleUploadedFile(
                name='sample.jpeg',
                content=open(os.path.join(os.environ['HOME'],'Pictures/sample.jpeg'), 'rb').read(),
                content_type='image/jpeg'
            )
        }
        form = SignUpForm(post_dict, files_dict)
        self.assertFalse(form.is_valid())

    def test_city_is_valid(self):
        city = 142
        post_dict = {
            'username':'tester',
            'password1':'testpassword',
            'password2':'testpassword',
            'email':'test@gmail.com',
            'prefecture':27,
            'city':city
        }
        files_dict = {
            'icon':SimpleUploadedFile(
                name='sample.jpeg',
                content=open(os.path.join(os.environ['HOME'],'Pictures/sample.jpeg'), 'rb').read(),
                content_type='image/jpeg'
            )
        }
        form = SignUpForm(post_dict, files_dict)
        self.assertFalse(form.is_valid())


class UserUpdateFormTest(TestCase):

    def test_icon_label(self):
        form = SignUpForm()
        self.assertTrue(form.fields['icon'].label == 'Icon')

    def test_form_is_valid(self):
        post_dict = {
            'username':'tester',
            'email':'test@gmail.com',
        }
        files_dict = {
            'icon':SimpleUploadedFile(
                name='sample.jpeg',
                content=open(os.path.join(os.environ['HOME'],'Pictures/sample.jpeg'), 'rb').read(),
                content_type='image/jpeg'
            )
        }
        form = UserUpdateForm(post_dict, files_dict)
        self.assertTrue(form.is_valid())
