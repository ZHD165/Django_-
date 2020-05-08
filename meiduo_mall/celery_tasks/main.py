# 从你刚刚下载的包中导入 Celery 类（拿到类不能直接使用！）

# 利用导入的 Celery 创建对象

from celery import Celery

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE','meiduo_mall.settings.dev')

celery_app = Celery('meiduo')

celery_app.config_from_object('celery_tasks.config')

# 自动注册 celery 任务
celery_app.autodiscover_tasks(['celery_tasks.sms', 'celery_tasks.email'])




celery_app.autodiscover_tasks(['celery_tasks.sms',
                                'celery_tasks.email',
                                'celery_tasks.html'])
