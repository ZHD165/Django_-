from django.contrib.auth.models import AbstractUser
from django.db import models
from itsdangerous import TimedJSONWebSignatureSerializer, BadData
from django.conf import settings

# Create your models here.
from meiduo_mall.utils.BaseModel import BaseModel


class User(AbstractUser):
    # 增加一个monile 字段；
    mobile = models.CharField(
        max_length=11,
        unique=True,
        verbose_name='电话号码'
    )
    email_active = models.BooleanField(
        default=False,
        verbose_name='邮箱是否激活'
    )
    # 新增
    default_address = models.ForeignKey(
        'Address',
        related_name='users',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='默认地址'
    )

    class Meta:
        db_table = 'tb_users'
        # 指定
        verbose_name = '用户表'
        # 如果是复数，则还是verbose_name
        verbose_name_plural = verbose_name


    def __str__(self):

        return self.username

    # 导入:

    def generate_access_token(self):
        """
        生成邮箱验证链接
        :param user: 当前登录用户
        :return: verify_url
        """
        # 调用 itsdangerous 中的类,生成对象
        # 有效期: 1天
        serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY,
                                                     expires_in=60 * 60 * 24)
        # 拼接参数
        data = {'user_id': self.id, 'email': self.email}
        # 加密生成 token 值, 这个值是 bytes 类型, 所以解码为 str:
        token = serializer.dumps(data).decode()
        # 拼接 url
        verify_url = settings.EMAIL_VERIFY_URL + token
        # print(verify_url)
        # 返回
        return verify_url

    # 定义验证函数:
    @staticmethod
    def check_verify_email_token(token):
        """
        验证token并提取user
        :param token: 用户信息签名后的结果
        :return: user, None
        """
        # 调用 itsdangerous 类,生成对象
        # 邮件验证链接有效期：一天
        serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY,
                                                     expires_in=60 * 60 * 24)
        try:
            # 解析传入的 token 值, 获取数据 data
            data = serializer.loads(token)
        except BadData:
            # 如果传入的 token 中没有值, 则报错
            return None
        else:
            # 如果有值, 则获取
            user_id = data.get('user_id')
            email = data.get('email')

            # 获取到值之后, 尝试从 User 表中获取对应的用户
        try:
            user = User.objects.get(id=user_id,
                                    email=email)
        except Exception as  e:
            # 如果用户不存在, 则返回 None
            return None
        else:
            # 如果存在则直接返回
            return user


# 增加地址的模型类, 放到User模型类的下方:
class Address(BaseModel):
    """
    用户地址
    """
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='addresses',
                             verbose_name='用户')

    province = models.ForeignKey('areas.Area',
                                 on_delete=models.PROTECT,
                                 related_name='province_addresses',
                                 verbose_name='省')

    city = models.ForeignKey('areas.Area',
                             on_delete=models.PROTECT,
                             related_name='city_addresses',
                             verbose_name='市')

    district = models.ForeignKey('areas.Area',
                                 on_delete=models.PROTECT,
                                 related_name='district_addresses',
                                 verbose_name='区')

    title = models.CharField(max_length=20, verbose_name='地址名称')
    receiver = models.CharField(max_length=20, verbose_name='收货人')
    place = models.CharField(max_length=50, verbose_name='地址')
    mobile = models.CharField(max_length=11, verbose_name='手机')
    tel = models.CharField(max_length=20,
                           null=True,
                           blank=True,
                           default='',
                           verbose_name='固定电话')

    email = models.CharField(max_length=30,
                             null=True,
                             blank=True,
                             default='',
                             verbose_name='电子邮箱')

    is_deleted = models.BooleanField(default=False, verbose_name='逻辑删除')

    class Meta:
        db_table = 'tb_address'
        verbose_name = '用户地址'
        verbose_name_plural = verbose_name
        ordering = ['-update_time']
'''说明：
Address 模型类中的外键指向 Areas / models 里面的 Area，指明外键 ForeignKey 时，可以使用字符串应用名.模型类名来定义
related_name 在进行反向关联查询时使用的属性，
如 city = models.ForeignKey('areas.Area', related_name='city_addresses')表示可以通过Area对象.
city_addresses属性获取所有相关的 city 数据。
ordering 表名在进行 Address 查询时，默认使用的排序方式'''
