"""ユーザー情報に関わるViewファイル"""

from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import DetailView, FormView, UpdateView
from django.contrib.auth.mixins import AccessMixin, UserPassesTestMixin

from django import forms
from accounts.models import User
from accounts.forms import SignUpForm, SignOutForm, UserUpdateForm



class UserMatchMixin(UserPassesTestMixin):
    """ユーザー認証
        リクエストユーザーと取り扱おうとする登録情報に該当するユーザーが一致するかを確認
        認証失敗で403例外を発生

    """

    def test_func(self):
        """リクエストユーザーとアクセスしようとする登録情報に紐づくユーザーが一致するかを確認

            Returns:
                Bool: Trueなら認証成功、Falseなら認証失敗

        """

        user = self.request.user
        return user.pk == self.kwargs['pk'] or user.is_superuser


class LogoutRequiredMixin(AccessMixin):
    """クライアントのログイン状態を確認し、ログイン時はアクセスを制限"""

    def dispatch(self, request, *args, **kwargs):
        """クライアントがログイン状態であればホームにリダイレクトされ、
            継承元のdispatch関数はリターンしない
        """
        if request.user.is_authenticated:
            return redirect('weatherapp:home')
        return super().dispatch(request, *args, **kwargs)


class SignUpView(LogoutRequiredMixin, FormView):
    """ユーザー登録のためのView"""
    model = User
    form_class = SignUpForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('weatherapp:home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        city = {
            0: [(0, '稚内'), (1, '旭川'), (2, '留萌')],
            1: [(3, '札幌'), (4, '岩見沢'), (5, '倶知安')],
            2: [(6, '網走'), (7, '北見'), (8, '紋別'), (9, '根室'), (10, '釧路'), (11, '帯広')],
            3: [(12, '室蘭'), (13, '浦河'), (14, '函館'), (15, '江差')],
            4: [(16, '青森'), (17, 'むつ'), (18, '八戸')],
            5: [(19, '盛岡'), (20, '宮古'), (21, '大船渡')],
            6: [(22, '仙台'), (23, '白石')],
            7: [(24, '秋田'), (25, '横手')],
            8: [(26, '山形'), (27, '米沢'), (28, '酒田'), (29, '新庄')],
            9: [(30, '福島'), (31, '小名浜'), (32, '若松')],
            10: [(33, '東京'), (34, '大島'), (35, '八丈島'), (36, '父島')],
            11: [(37, '横浜'), (38, '小田原')],
            12: [(39, 'さいたま'), (40, '熊谷'), (41, '秩父')],
            13: [(42, '千葉'), (43, '銚子'), (44, '館山')],
            14: [(45, '水戸'), (46, '土浦')],
            15: [(47, '宇都宮'), (48, '大田原')],
            16: [(49, '前橋'), (50, 'みなかみ')],
            17: [(51, '甲府'), (52, '河口湖')],
            18: [(53, '新潟'), (54, '長岡'), (55, '高田'), (56, '相川')],
            19: [(57, '長野'), (58, '松本'), (59, '飯田')],
            20: [(60, '名古屋'), (61, '豊橋')],
            21: [(62, '岐阜'), (63, '高山')],
            22: [(64, '静岡'), (65, '網代'), (66, '三島'), (67, '浜松')],
            23: [(68, '津'), (69, '尾鷲')],
            24: [(70, '富山'), (71, '伏木')],
            25: [(72, '金沢'), (73, '輪島')],
            26: [(74, '福井'), (75, '敦賀')],
            27: [(76, '大阪')],
            28: [(77, '神戸'), (78, '豊岡')],
            29: [(79, '京都'), (80, '舞鶴')],
            30: [(81, '大津'), (82, '彦根')],
            31: [(83, '奈良'), (84, '風屋')],
            32: [(85, '和歌山'), (86, '潮岬')],
            33: [(87, '松江'), (88, '浜田'), (89, '西郷')],
            34: [(90, '鳥取'), (91, '米子')],
            35: [(92, '岡山'), (93, '津山')],
            36: [(94, '広島'), (95, '庄原')],
            37: [(96, '下関'), (97, '山口'), (98, '柳井'), (99, '萩')],
            38: [(100, '徳島'), (101, '日和佐')],
            39: [(102, '高松')],
            40: [(103, '松山'), (104, '新居浜'), (105, '宇和島')],
            41: [(106, '高知'), (107, '室戸岬'), (108, '清水')],
            42: [(109, '福岡'), (110, '八幡'), (111, '飯塚'), (112, '久留米')],
            43: [(113, '佐賀'), (114, '伊万里')],
            44: [(115, '長崎'), (116, '佐世保'), (117, '厳原'), (118, '福江')],
            45: [(119, '熊本'), (120, '阿蘇乙姫'), (121, '牛深'), (122, '人吉')],
            46: [(123, '大分'), (124, '中津'), (125, '日田'), (126, '佐伯')],
            47: [(127, '宮崎'), (128, '延岡'), (129, '都城'), (130, '高千穂')],
            48: [(131, '名瀬'), (132, '鹿児島'), (133, '鹿屋'), (134, '種子島')],
            49: [(135, '那覇'), (136, '名護'), (137, '久米島'), (138, '南大東'), (139, '宮古島'), (140, '石垣島'), (141, '与那国島')]
        }


        if self.request.method == 'GET':
            context['initial'] = True
        else:
            if self.request.POST.get('button') == 'choice':
                choices = city[int(self.request.POST.get('prefecture'))]

                initial = {
                    'prefecture':self.request.POST.get('prefecture'),
                    }
                form = SignUpForm(initial=initial)
                form.fields['city'].widget = forms.Select(choices=choices)
                context['form'] = form
        return context


    def form_valid(self, form):
        if self.request.POST.get('button') == 'register':
            form.save()
            messages.success(self.request, '登録完了です')
        return super().form_valid(form)


    def form_invalid(self, form):
        if self.request.POST.get('button') == 'register':
            messages.error(self.request, '登録に失敗しました')
        return super().form_invalid(form)


class SignOutView(UserMatchMixin, FormView):
    model = User
    form_class = SignOutForm
    template_name = 'registration/signout.html'
    success_url = reverse_lazy('weatherapp:home')

    def form_valid(self, form):
        user = User.objects.get(id=self.request.user.id)
        if not user.is_superuser:
            user.is_active = False
            user.save()
            messages.success(self.request, '退会手続きが完了しました')
        return super().form_valid(form)


class UserUpdateView(UserMatchMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'registration/user_update.html'

    def get_success_url(self):
        return reverse_lazy('accounts:detail', kwargs={'pk':self.kwargs['pk']})

    def form_valid(self, form):
        messages.success(self.request, 'ユーザー情報を更新しました')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, '更新に失敗しました')
        return super().form_invalid(form)

class UserDetailView(UserMatchMixin, DetailView):
    model = User
    template_name = 'registration/user_detail.html'
