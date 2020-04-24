import logging
import random
from django import http
from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection
from django.http import HttpResponse
from meiduo_mall.libs.captcha.captcha import captcha

logger = logging.getLogger('django')
from meiduo_mall.libs.yuntongxun.ccp_sms import CCP
from celery_tasks.sms.tasks import ccp_send_sms_code


class ImageCodeView(View):

    def get(self, request, uuid):
        '''生成图形验证码,保存后返回'''
        # 1.调用captcha框架,生成图片和对应的信息
        text, image = captcha.generate_captcha()

        # 2.链接redis, 获取redis的链接对象
        redis_conn = get_redis_connection('verify_code')
        # 3.调用链接对象, 把数据保存到redis
        redis_conn.setex('img_%s' % uuid, 300, text)

        # 4.返回图片给前端
        return HttpResponse(image,
                            content_type='image/jpg')


class SMSCodeView(View):

    def get(self, reqeust, mobile):
        '''   '''
        # 额外增加的功能
        # 0.从redis中获取60s保存的信息
        # redis_conn = get_redis_connection('verify_code')
        # flag = redis_conn.get('flag_%s' % mobile)
        # if flag:
        #     return JsonResponse{'code':400,
        #                         'errmsg':'比传参数不为空'}
        redis_conn = get_redis_connection('verify_code')

        send_flag = redis_conn.get('send_flag_%s' % mobile)
        if send_flag:
            return http.JsonResponse({'code': 400,
                                      'errmsg': '发送短信过于频繁'})
        """
           :param reqeust: 请求对象
           :param mobile: 手机号
           :return: JSON
           """
        # 1. 接收参数
        image_code_client = reqeust.GET.get('image_code')
        uuid = reqeust.GET.get('image_code_id')
        # all 任意一个为空，则为Fslse

        # 2. 校验参数
        if not all([image_code_client, uuid]):
            return http.JsonResponse({'code': 400,
                                      'errmsg': '缺少必传参数'})
        # 3. 创建连接到redis的对象
        image_code_server = redis_conn.get('img_%s' % uuid)
        # 4. 提取图形验证码 #
        if image_code_server is None:
            return http.JsonResponse({'code': 400,
                                      'errmsg': '图形验证码失效'})
        # 5. 删除图形验证码，避免恶意测试图形验证码
        try:
            redis_conn.delete('img_%s' % uuid)
        except Exception as e:
            logger.info(e)

        # 6. 对比图形验证码
        # bytes 转字符串
        image_code_server = image_code_server.decode()
        # 转小写后比较
        if image_code_client.lower() != image_code_server.lower():
            # 图形验证码过期或者不存在
            return http.JsonResponse({'code': 400,
                                      'errmsg': '输入图形验证码有误'})

        # 7. 生成短信验证码：生成6位数验证码
        sms_code = '%06d' % random.randint(0, 999999)
        logger.info(sms_code)

        # 创建redis管道对象:
        pl = redis_conn.pipeline()
        # 8. 保存短信验证码
        # 短信验证码有效期，单位：300秒
        # redis_conn.setex('sms_%s' % mobile, 300, sms_code)
        #将redis 请求添加到队列
        pl.setex('sms_%s' % mobile, 300, sms_code)

        # redis_conn.setex('send_flag_%s' % mobile, 60, 1)
        pl.setex('send_flag_%s' % mobile, 60, 1)

        # 执行管道:
        pl.execute()
        # 9. 发送短信验证码

        # 短信模板
        # CCP().send_template_sms(mobile, [sms_code, 5], 1)
        #添加一个提示celery 抛出任务的提醒
        ccp_send_sms_code.delay(mobile, sms_code)
        # 10. 响应结果
        return http.JsonResponse({'code': 0,
                                  'errmsg': '发送短信成功'})
