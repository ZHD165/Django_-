# 从你刚刚下载的包中导入 Celery 类（拿到类不能直接使用！）
from celery import Celery

# 利用导入的 Celery 创建对象
celery_app = Celery('meiduo')

celery_app.config_from_object('celery_tasks.config')
# 让 celery_app 自动捕获目标地址下的任务:
# 就是自动捕获 tasks
celery_app.autodiscover_tasks(['celery_tasks.sms'])

from celery import Celery

import os

if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'meiduo_mall.settings.dev'

celery_app = Celery('meiduo')

celery_app.config_from_object('celery_tasks.config')

# 自动注册 celery 任务
celery_app.autodiscover_tasks(['celery_tasks.sms', 'celery_tasks.email'])
