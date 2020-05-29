from django.contrib.auth.backends import ModelBackend
import re

from users.models import User
def get_user_by_account(account):
    '''判断 account 是否是手机号, 返回 user 对象'''
    try:
        if re.match('^1[3-9]\d{9}$', account):
            # account 是手机号
            # 根据手机号从数据库获取 user 对象返回.
            user = User.objects.get(mobile=account)
        else:
            # account 是用户名
            # 根据用户名从数据库获取 user 对象返回.
            user = User.objects.get(username=account)
    except Exception as e:
        # User.DoesNotExist:
        # 如果 account 既不是用户名也不是手机号
        # 我们返回 None
        return None
    else:
        # 如果得到 user, 则返回 user
        return user


class UsernameMobileAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        '''重写认证函数:使其具有手机号的认证功能'''

        """
            问题： 
            meihao 这个账户应该只能登录 前端
            不能应该登录 后台

            meihao 既可以登录后台 也可以登录前端
            1. 因为 DRF 和 Django用的一套认证  （肯定是同一个表）

            2. 该如何区分 后端登录  和 前端登录
                前端登录 --> 手机号，用户名登录    login/
                后端登录 --> 用户名               meiduo_admin/authorizations/

            3. 最终都会到 我们自定义的认证这里
            4.  
                后台用户的一个 is_superuser(管理员) 标记必须为True
            """
        # 到底该如何区分谁是前端，谁是后端
        if request is None:
            # 后台用户走 后台验证逻辑
            # 后台验证
            try:
                admin_user = User.objects.get(username=username,is_staff =True)
            except:
                return  None
            #   验证密码 并且 验证权限
            if admin_user.check_password(password) and admin_user.is_superuser:
                return admin_user

        else:
            # 普通用户还走原来的业务逻辑
            # 自定义一个函数,用来区分username保存的类型: username/mobile
            user = get_user_by_account(username)

            if user and user.check_password(password):
                return user













































