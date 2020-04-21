from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View

from users.models import User


class UsernameCountView(View):
    def get(self, request, username):
        '''接受用户名，判断该用户名是否可以重复注册'''

        # 1.访问数据库，查看该username 是否有多个，把结果赋给一个变量！

        try:
            count = User.objects.filter(username=username).count()
        # 2.如果没有问题，返回json
        except Exception as e:
            return JsonResponse({'code': 400,
                                 'errmsg': '访问数据库失败！'})
        # 3.如果有问题，返回json！
        return JsonResponse({'code': 0,
                             'errmsg': 'ok',
                             'count': count})


class MobileCountView(View):
    def get(self, request, mobile):
        '''判断手机号是否重复注册'''
        # 1.查询mobile在mysql中的个数
        try:
            count = User.objects.filter(mobile=mobile).count()
        except Exception as  e:
            return JsonResponse({'code': 400,
                                 'errmg': '查询数据库出错'})
        # 2.返回结果（json）
        return JsonResponse({'code': 0,
                             'errmsg': 'ok',
                             'count': count})
