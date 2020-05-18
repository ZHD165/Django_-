import json
import re
import logging

from carts.utils import merge_cookie_to_redis
from goods.models import SKU
from users.models import User, Address

logger = logging.getLogger('django')
from django import http
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
            return JsonResponse({'code': 400,
                                 'errmsg': '保存到数据库出错'})
        login(request, user)
        # 13.拼接json返回
        # 生成响应对象
        response = JsonResponse({'code': 0,
                                 'errmsg': 'ok'})

        # 在响应对象中设置用户名信息.
        # 将用户名写入到 cookie，有效期 14 天
        # response.set_cookie('username',
        #                     user.username,
        #                     max_age=3600 * 24 * 14)
        # 增加合并购物车功能
        response = merge_cookie_to_redis(request, response)

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

        # 增加合并购物车功能
        response = merge_cookie_to_redis(request, response)

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


class UserInfoView(LoginRequiredMixin, View):

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
            return JsonResponse({'code': 400,
                                 'errmsg': '缺少token'})

        # 调用上面封装好的方法, 将 token 传入
        user = User.check_verify_email_token(token)
        if not user:
            return http.JsonResponse({'code': 400,
                                      'errmsg': '无效的token'})

        # 修改 email_active 的值为 True
        try:
            user.email_active = True
            user.save()
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': 400,
                                 'errmsg': '激活邮件失败'})

        # 返回邮箱验证结果
        return JsonResponse({'code': 0,
                             'errmsg': 'ok'})


class CreateAddressView(View):
    """新增地址"""

    def post(self, request):
        """实现新增地址逻辑"""

        # 获取地址个数:
        try:
            count = Address.objects.filter(user=request.user,
                                           is_deleted=False).count()
        except Exception as e:
            return JsonResponse({'code': 400,
                                 'errmsg': '获取地址数据出错'})
        # 2.判断是否超过地址上限：最多20个
        if count >= 20:
            return JsonResponse({'code': 400,
                                 'errmsg': '超过地址20个上限'})

        # 3.接收参数（json）
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        # 4.总体校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return JsonResponse({'code': 400,
                                 'errmsg': '缺少必传参数'})

        # 5.单个检验mobile
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return JsonResponse({'code': 400,
                                 'errmsg': '参数mobile有误'})
        # 6.tel
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return JsonResponse({'code': 400,
                                     'errmsg': 'tel格式不正确'})
        # 7.email
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return JsonResponse({'code': 400,
                                     'errmsg': '参数email有误'})

        # 8.往address表中增加地址信息
        try:
            # create方法增加
            address = Address.objects.create(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )

            # 9.判断默认地址是否存在，如果不存在，把刚刚增加的地址作为默认地址
            if not request.user.default_address:
                request.user.default_address = address
                request.user.save()

        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': 400,
                                 'errmsg': '新增地址失败'})

        # 新增地址成功，将新增的地址响应给前端实现局部刷新
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }

        # 响应保存结果
        return JsonResponse({'code': 0,
                             'errmsg': '新增地址成功',
                             'address': address_dict})


class AddressView(View):
    def get(self, request):
        '''前端发送get请求，获取地址信息的借口'''

        try:
            # 1.从mysql中获取该用户的所有未删除的地址信息
            addresses = Address.objects.filter(user=request.user,
                                               is_deleted=False)
        except Exception as  e:
            return JsonResponse({'code': 400,
                                 'errmsg': '从地址列表中获取不到地址信息'})
        list = []
        # 2.遍历这些地址信息，获取每一个地址
        for address in addresses:
            # 3.把每一个地址信息==> {} ===>[]
            dict = {
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "city": address.city.name,
                "district": address.district.name,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email

            }

            if request.user.default_address.id == address.id:
                # 4.判断该地址信息是否是默认地址，如果是，增加到[]的第一个
                # 默认地址：
                list.insert(0, dict)
            else:
                # 5.如果不是，追加到[]的后面
                list.append(dict)

        deault_address_id = request.user.default_address_id

        # 6. 拼接参数，返回json
        return JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'default_address_id': deault_address_id,
            'addresses': list
        })


class UpdateDestroyAddressView(View):

    def put(self, request, address_id):
        '''修改地址的借口'''
        # 1.接受前端传来的数据
        dict = json.loads(request.body.decode())
        receiver = dict.get('receiver')
        province_id = dict.get('province_id')
        city_id = dict.get('city_id')
        district_id = dict.get('district_id')
        place = dict.get('place')
        mobile = dict.get('mobile')
        tel = dict.get('tel')
        email = dict.get('email')
        # 2.检验数据
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return JsonResponse({'code': 400,
                                 'errmsg': '缺少必传参数'})

            # 5.单个检验mobile
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return JsonResponse({'code': 400,
                                 'errmsg': 'mobile格式不正确'})

            # 6.tel
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return JsonResponse({'code': 400,
                                     'errmsg': 'tel格式不正确'})
            # 7.email
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return JsonResponse({'code': 400,
                                     'errmsg': 'email格式不正确'})

        # 3.获取address_id对应的查询集.调用查询集的update方法,更新
        try:
            address = Address.objects.filter(id=address_id).update(
                user=request.user,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                title=receiver,
                receiver=receiver,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )
        except Exception as e:
            return JsonResponse({'code': 400,
                                 'errmsg': '更新失败'})

        # 4.拼接参数, 返回
        address = Address.objects.get(id=address_id)
        dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }

        return JsonResponse({'code': 0,
                             'errmsg': 'ok',
                             'address': dict})

    def delete(self, request, address_id):
        # 1.查询要删除的地址
        try:
            address = Address.objects.get(id=address_id)
            # 2.降低至逻辑删除设置为True
            address.is_deleted = True

            address.save()
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': 400,
                                 'errmsg': '删除地址失败'})

        return JsonResponse({'code': 0,
                             'errmsg': '删除地址成功'})


class DefaultAddressView(View):
    '''设置默认地址'''

    def put(self, request, address_id):
        '''设置默认地址'''
        try:
            # 1.接收参数，查询地址
            address = Address.objects.get(id=address_id)

            # 设置默认地址
            request.user.default_address = address
            request.user.save()
        except Exception as  e:
            logger.error(e)
            return JsonResponse({'code': 400,
                                 'errmsg': '设置默认地址失败'})
        return JsonResponse({'code': 0,
                             'errmsg': '设置默认地址成功'})


class UpdateTitleAddressView(View):
    '''设置标题地址'''

    def put(self, request, address_id):

        # 1. 接受参数：地址标题
        json_dict = json.loads(request.body.decode())
        title = json_dict.get('title')

        try:
            # 查询地址
            address = Address.objects.get(id=address_id)

            # 设置新的标题

            address.title = title
            address.save()
        except Exception as  e:
            logger.error(e)
            return JsonResponse({'code': 400,
                                 'errmsg': '设置地址标题失败'})

        # 相应删除地址结果
        return JsonResponse({
            'code': 0,
            'errmsg': '设置地址标题成功'
        })


class ChangePasswordView(LoginRequiredMixin, View):
    '''修改密码'''

    def put(self, request):
        '''实现修改密码逻辑'''
        # 接收参数
        dict = json.loads(request.body.decode())
        old_password = dict.get('old_password')
        new_password = dict.get('new_password')
        new_password2 = dict.get('new_password2')

        # 参数效验

        if not all([old_password, new_password, new_password2]):
            return JsonResponse({'code': 400,
                                 'errmsg': '缺少必传参数'})

        result = request.user.check_password(old_password)
        if not result:
            return JsonResponse({'code': 400,
                                 'errmsg': '原始密码不正确'})
        if not re.match(r'^[0-9A-Za-z]{8,20}$', new_password):
            return http.JsonResponse({'code': 400,
                                      'errmsg': '密码最少8位,最长20位'})

        if new_password != new_password2:
            return http.JsonResponse({'code': 400,
                                      'errmsg': '两次输入密码不一致'})

        # 修改密码
        try:
            request.user.set_password(new_password)
            request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': 400,
                                      'errmsg': '修改密码失败'})

        # 清理状态保持信息
        logout(request)

        response = http.JsonResponse({'code': 0,
                                      'errmsg': 'ok'})

        response.delete_cookie('username')

        # # 响应密码修改结果：重定向到登录界面
        return response


class UserBrowseHistory(View):
    """用户浏览记录"""

    def post(self, request):
        """保存用户浏览记录"""
        # 接收参数
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')

        # 校验参数:
        from goods.models import SKU
        try:

            SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:

            return http.HttpResponseForbidden('sku不存在')

        # 3.链接redis，获取redis 的链接对象
        redis_conn = get_redis_connection('history')
        pl = redis_conn.pipeline()
        user_id = request.user.id

        # 4.调用链接对象，先去重: 这里给 0 代表去除所有的 sku_id
        pl.lrem('history_%s' % user_id, 0, sku_id)
        # 再存储
        pl.lpush('history_%s' % user_id, sku_id)
        # 最后截取: 界面有限, 只保留 5 个
        pl.ltrim('history_%s' % user_id, 0, 4)
        # 执行管道
        pl.execute()

        # 响应结果
        return JsonResponse({'code': 0,
                             'errmsg': 'OK'})

    def get(self, request):
        """获取用户浏览记录"""
        # 获取Redis存储的sku_id列表信息
        redis_conn = get_redis_connection('history')
        sku_ids = redis_conn.lrange('history_%s' % request.user.id, 0, -1)

        # 根据sku_ids列表数据，查询出商品sku信息
        skus = []
        for sku_id in sku_ids:
            sku = SKU.objects.get(id=sku_id)
            skus.append({
                'id': sku.id,
                'name': sku.name,
                'default_image_url': sku.default_image_url,
                'price': sku.price
            })

        return http.JsonResponse({'code': 0,
                                  'errmsg': 'OK',
                                  'skus': skus})
