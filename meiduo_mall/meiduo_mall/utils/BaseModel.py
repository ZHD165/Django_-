# 这里的代码主要作为别的模型类的基类来使用.增加数据新建时间和更新时间:

from django.db import models


class BaseModel(models.Model):
    """为模型类补充字段"""

    # 创建时间:
    create_time = models.DateTimeField(auto_now_add=True,
                                       verbose_name="创建时间")
    # 更新时间:
    update_time = models.DateTimeField(auto_now=True,
                                       verbose_name="更新时间")

    class Meta:
        # 说明是抽象模型类(抽象模型类不会创建表)
        abstract = True
# 上面代码中相关参数解读:
# auto_now_add:创建或添加对象时自动添加时间, 修改或更新对象时, 不会更改时间
#  auto_now:凡是对对象进行操作(创建/添加/修改/更新),时间都会随之改变
# abstract:声明该模型类仅继承使用，数据库迁移时不会创建 BaseModel 的表
