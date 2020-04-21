from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r'^image_codes/(?P<uuid>[\w-]+)/$',views.ImageCodeView.as_view()),
    # 获取短信验证码的子路由:
    re_path(r'^sms_codes/(?P<mobile>1[3-9]\d{9})/$', views.SMSCodeView.as_view())
]