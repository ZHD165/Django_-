# 如果使用 redis 作为中间人
# 需要这样配置:
broker_url = 'redis://127.0.0.1:6379/3'

from celery import Celery

celery_app = Celery('meiduo')

# 将刚刚的 config 配置给 celery
# 里面的参数为我们创建的 config 配置文件:
celery_app.config_from_object('celery_tasks.config')
