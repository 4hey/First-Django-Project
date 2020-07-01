"""ユーザー登録に関するurls.py"""
from django.urls import path
from accounts.views import SignUpView, SignOutView, UserDetailView, UserUpdateView

app_name = 'accounts'

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('<int:pk>/signout/', SignOutView.as_view(), name='signout'),
    path('<int:pk>/detail/', UserDetailView.as_view(), name='detail'),
    path('<int:pk>/update/', UserUpdateView.as_view(), name='update'),
    ]
