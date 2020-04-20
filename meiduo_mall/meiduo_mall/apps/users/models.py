from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
    #增加一个monile 字段；
    mobile = models.CharField(max_length=11,unique=True,verbose_name='电话号码')

    class Meta:
        db_table = 'tb_users'
        #指定
        verbose_name = '用户表'
        #如果是复数，则还是verbose_name
        verbose_name_plural = verbose_name

