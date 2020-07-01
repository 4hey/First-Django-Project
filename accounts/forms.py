"""ユーザー登録情報に関するフォームの定義"""

from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from accounts.models import User

class SignUpForm(UserCreationForm):
    """新規登録フォーム"""

    class Meta:
        model = User
        fields = ['prefecture', 'city', 'username', 'email', 'icon']


class UserUpdateForm(UserChangeForm):
    """登録情報の更新フォーム"""

    password = None

    class Meta:
        model = User
        fields = ['username', 'email', 'icon']

class SignOutForm(UserChangeForm):
    """退会フォーム"""

    password = None

    class Meta:
        model = User
        fields = ['is_active']
