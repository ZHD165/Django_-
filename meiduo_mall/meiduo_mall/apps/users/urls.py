"""meiduo_mall URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
from django.urls import  include, re_path

from . import views

urlpatterns = [
    re_path(r'^usernames/(?P<username>\w{5,20})/count/$', views.UsernameCountView.as_view()),

    re_path(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),
# 注册
    re_path(r'^register/$', views.RegisterView.as_view()),
    # 用户名登录的子路由:
    re_path(r'^login/$', views.LoginView.as_view()),
# 退出登录
    re_path(r'^logout/$', views.LogoutView.as_view()),
# 用户中心的子路由
    re_path(r'^info/$', views.UserInfoView.as_view()),
]
