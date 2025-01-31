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
    # 添加邮箱
    re_path(r'^emails/$', views.EmailView.as_view()),
    # 验证邮箱
    re_path(r'^emails/verification/$', views.VerifyEmailView.as_view()),
    # 新增收货地址
    re_path(r'^addresses/create/$', views.CreateAddressView.as_view()),
    # 访问地址的子路由:
    re_path(r'^addresses/$', views.AddressView.as_view()),
    # 修改和删除收货地址
    re_path(r'^addresses/(?P<address_id>\d+)/$', views.UpdateDestroyAddressView.as_view()),
    # 修改和删除收货地址
    re_path(r'^addresses/(?P<address_id>\d+)/$', views.UpdateDestroyAddressView.as_view()),
    # 设置默认地址
    re_path(r'^addresses/(?P<address_id>\d+)/default/$', views.DefaultAddressView.as_view()),
    # 更新地址标题
    re_path(r'^addresses/(?P<address_id>\d+)/title/$', views.UpdateTitleAddressView.as_view()),
    # 修改密码
    re_path(r'^password/$', views.ChangePasswordView.as_view()),
    re_path(r'^browse_histories/$',views.UserBrowseHistory.as_view())
]
