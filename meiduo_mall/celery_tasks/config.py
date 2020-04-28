# 如果使用 redis 作为中间人
# 需要这样配置:
broker_url = 'redis://127.0.0.1:6379/3'#2号库被验证码使用了！

# from celery import Celery
#
# celery_app = Celery('meiduo_mall')
#
# # 将刚刚的 config 配置给 celery
# # 里面的参数为我们创建的 config 配置文件:
# celery_app.config_from_object('celery_tasks.config')


'''
如果使用 redis 作为中间人
需要这样配置:
broker_url='redis://127.0.0.1:6379/3'

如果使用别的作为中间人, 例如使用 rabbitmq
则 rabbitmq 配置如下:
broker_url= 'amqp://用户名:密码@ip地址:5672'

例如: 
    meihao: 在rabbitq中创建的用户名, 注意: 远端链接时不能使用guest账户.
    123456: 在rabbitq中用户名对应的密码
    ip部分: 指的是当前rabbitq所在的电脑ip
    5672: 是规定的端口号
    broker_url = 'amqp://meihao:123456@172.16.238.128:5672'

说明:
    上面的配置, 选择一个即可, 我们这里使用的是 redis
    如果以后进入公司, 使用的不是 redis 作为存储的中间人.
    则可以像我下面设置的那样, 设置别的工具作为中间人, 例如: rabbitmq
'''