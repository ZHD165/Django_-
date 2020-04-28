import json
import re
import logging

logger = logging.getLogger('django')
from django import http
from users.models import User
from django.views import View
from django.contrib.auth import login, logout
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from meiduo_mall.utils.views import LoginRequiredMixin
from django_redis import get_redis_connection
from django.contrib.auth import login, authenticate
# from .utils import generate_access_token
# 从 celery_tasks 中导入:
from celery_tasks.email.tasks import send_verify_email
class UsernameCountView(View):
    def get(self, request, username):
        '''接受用户名，判断该用户名是否可以重复注册'''

        # 1.访问数据库，查看该username 是否有多个，把结果赋给一个变量！

        try:
            count = User.objects.filter(username=username).count()
        # 3.如果有问题，返回json
        except Exception as e:
            return JsonResponse({'code': 400,
                                 'errmsg': '访问数据库失败！'})
        # 2.如果没有问题，返回json！
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


class RegisterView(View):

    def post(self, request):
        '''接收参数, 保存到数据库'''
        # 1.接收参数
        dict = json.loads(request.body.decode())
        username = dict.get('username')
        password = dict.get('password')
        password2 = dict.get('password2')
        mobile = dict.get('mobile')
        allow = dict.get('allow')
        sms_code_client = dict.get('sms_code')

        # 2.校验(整体)
        if not all([username, password, password2, mobile, allow, sms_code_client]):
            return http.JsonResponse({'code': 400,
                                      'errmsg': '缺少必传参数'})

        # 3.username检验
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return http.JsonResponse({'code': 400,
                                      'errmsg': 'username格式有误'})

        # 4.password检验
        if not re.match(r'^[a-zA-Z0-9]{8,20}$', password):
            return http.JsonResponse({'code': 400,
                                      'errmsg': 'password格式有误'})

        # 5.password2 和 password
        if password != password2:
            return http.JsonResponse({'code': 400,
                                      'errmsg': '两次输入不对'})
        # 6.mobile检验
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.JsonResponse({'code': 400,
                                      'errmsg': 'mobile格式有误'})
        # 7.allow检验
        if allow != True:
            return http.JsonResponse({'code': 400,
                                      'errmsg': 'allow格式有误'})

        # 8.sms_code检验 (链接redis数据库)
        redis_conn = get_redis_connection('verify_code')

        # 9.从redis中取值
        sms_code_server = redis_conn.get('sms_%s' % mobile)

        # 10.判断该值是否存在
        if not sms_code_server:
            return http.JsonResponse({'code': 400,
                                      'errmsg': '短信验证码过期'})
        # 11.把redis中取得值和前端发的值对比
        if sms_code_client != sms_code_server.decode():
            return http.JsonResponse({'code': 400,
                                      'errmsg': '验证码有误'})

        # 12.保存到数据库 (username password mobile)
        try:
            user = User.objects.create_user(username=username,
                                            password=password,
                                            mobile=mobile)
        except Exception as e:
            return http.JsonResponse({'code': 400,
                                      'errmsg': '保存到数据库出错'})
        login(request, user)
        # 13.拼接json返回
        # 生成响应对象
        response = http.JsonResponse({'code': 0,
                                      'errmsg': 'ok'})

        # 在响应对象中设置用户名信息.
        # 将用户名写入到 cookie，有效期 14 天
        response.set_cookie('username',
                            user.username,
                            max_age=3600 * 24 * 14)

        # 返回响应结果
        return response


class LoginView(View):

    def post(self, request):
        '''实现登录功能'''

        # 1.接收json参数, 获取每一个
        dict = json.loads(request.body.decode())
        username = dict.get('username')
        password = dict.get('password')
        remembered = dict.get('remembered')

        # 2.总体检验, 查看是否为空
        if not all([username, password]):
            return JsonResponse({'code': 400,
                                 'errmsg': '缺少必传参数'})

        # 3.username检验
        # if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
        #     return JsonResponse({'code': 400,
        #                          'errmsg': 'username格式有误'})

        # 4.password检验
        if not re.match(r'^[a-zA-Z0-9]{8,20}$', password):
            return JsonResponse({'code': 400,
                                 'errmsg': 'password格式有误'})

        # 5.remembered检验是否为bool类型:
        if remembered:
            if not isinstance(remembered, bool):
                return JsonResponse({'code': 400,
                                     'errmsg': 'remembered不是bool类型'})

        # 6.登录认证(authenticate), 获取用户
        user = authenticate(username=username,
                            password=password)

        # 7.判断该用户是否存在
        if not user:
            return JsonResponse({'code': 400,
                                 'errmsg': '用户名或者密码错误'})
        # 8.状态保持
        login(request, user)

        # 9.判断是否需要记住用户
        if remembered != True:
            # 11.如果不需要: 设置seesion有效期: 关闭浏览器立刻过期
            request.session.set_expiry(0)
        else:
            # 10.如果需要: 设置sesion有效期: 两周
            request.session.set_expiry(None)

        response = JsonResponse({'code': 0,
                                 'errmsg': 'ok'})

        # response.set_cookie(key, value, max_age)
        response.set_cookie('username', user.username, max_age=3600 * 24 * 14)

        # 12.返回状态
        return response







# 取消登录，秩序传入request，删除session & sessionid，手动删除coogkie（username）
class LogoutView(View):
    """定义退出登录的接口"""

    def delete(self, request):
        """实现退出登录逻辑"""

        # 删除 session ：logout（request）
        logout(request)

        # 创建 response 对象.
        response = JsonResponse({'code': 0,
                                'errmsg': 'ok'})

        # 清除cookie（username），调用对象的 delete_cookie 方法, 清除cookie
        response.delete_cookie('username')

        # 返回响应
        return response

    # 给该类视图增加 Mixin 扩展类


class UserInfoView(LoginRequiredMixin,View):

    def get(self, request):
        '''只有登录用户才能进入该类视图'''
        dict = {
            "username": request.user.username,
            "mobile": request.user.mobile,
            "email": request.user.email,
            "email_active": request.user.email_active
        }

        return JsonResponse({'code': 0,
                             'errmsg': 'ok',
                             'info_data': dict})


class EmailView(View):
    def put(self, request):

        '''保存数据哭'''
        # 1.接受参数
        dict = json.loads(request.body.decode())
        email = dict.get('email')
        # 2.检验参数：判断该参数是否有值
        if not email:
            return JsonResponse({'code': 400,
                                 'errmsg': '缺少必传参数'})
        # 3.检验email的格式
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return JsonResponse({'code': 400,
                                 'errmsg': 'email格式不正确'})
        try:

            # 4.把前端发送的email复制给用户
            request.user.email = email
            # 5.保存
            request.user.save()
        except Exception as  e:
            logger.error(e)
            return JsonResponse({'code': 400,
                                      'errmsg': '添加邮箱失败'})

            # 响应添加邮箱结果

        # 6.给挡墙邮箱发送一份信
            # # 调用发送的函数:
            # # 用定义好的函数替换原来的字符串:
        verify_url = request.user.generate_access_token()
        # # 发送验证链接:
        send_verify_email.delay(email, verify_url)
        # 7.返回json 结果

        return JsonResponse({'code': 0,
                            'errmsg': '添加邮箱成功'})


class VerifyEmailView(View):
    """验证邮箱"""

    def put(self, request):
        ''''''
        """实现邮箱验证逻辑"""
        # 接收参数
        token = request.GET.get('token')

        # 校验参数：判断 token 是否为空和过期，提取 user
        if not token:
            return JsonResponse({'code':400,
                                  'errmsg':'缺少token'})

        # 调用上面封装好的方法, 将 token 传入
        user = User.check_verify_email_token(token)
        if not user:
            return http.JsonResponse({'code':400,
                                  'errmsg':'无效的token'})

        # 修改 email_active 的值为 True
        try:
            user.email_active = True
            user.save()
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code':400,
                                  'errmsg':'激活邮件失败'})

        # 返回邮箱验证结果
        return JsonResponse({'code':0,
                                  'errmsg':'ok'})

