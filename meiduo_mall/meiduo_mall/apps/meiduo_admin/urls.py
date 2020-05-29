



# obtain_jwt_token就是验证用户名和密码，没有问题会返回tocken
# 就是后台登录接口
# ...
# meiduo_admin/
from django.conf.urls import re_path
from rest_framework.routers import DefaultRouter
from rest_framework_jwt.views import obtain_jwt_token


from meiduo_admin.views import home, users, image, sku, order, spu, option, specs, brand, permission

urlpatterns = [
    re_path(r'^meiduo_admin/authorizations/$', obtain_jwt_token),

    re_path(r'^meiduo_admin/statistical/total_count/$', home.TotalCountView.as_view()),
    re_path(r'^meiduo_admin/statistical/day_active/$', home.UserDayActiveAPIView.as_view()),
    re_path(r'^meiduo_admin/statistical/day_orders/$', home.UserOrderInfoCountAPIView.as_view()),
    re_path(r'^meiduo_admin/statistical/month_increment/$', home.MonthUserView.as_view()),
    re_path(r'^meiduo_admin/statistical/day_increment/$', home.DayUserView.as_view()),
    # re_path(r'^meiduo_admin/detail/visit/(?P<category_id>\d+)/$', home.DetailVisitView.as_view()),
    # 统计作业题路由
    # 作业 日增用户
    # re_path(r'^statistical/day_increment/$', home.UserDailyCountView.as_view()),
    # 作业 日分类商品访问量
    re_path(r'^meiduo_admin/statistical/goods_day_views/$', home.UserCategoryCountAPIView.as_view()),
# 用户管理
    re_path(r'^meiduo_admin/users/$',users.UserListAPIView.as_view()),
    #图片管理
    re_path(r'^meiduo_admin/skus/simple/$',image.SimpleSKUListAPIView.as_view()),
    #SKU获取三级分类
    re_path(r'^meiduo_admin/skus/categories/$',sku.CategoryAPIView.as_view()),
    #获取所有spu数据
    re_path(r'^meiduo_admin/goods/simple/$',sku.SPUListAPIView.as_view()),


    re_path(r'^meiduo_admin/goods/(?P<pk>\d+)/specs/$',sku.GoodsSpecAPIView.as_view()),
    # 商品作业
    re_path(r'^meiduo_admin/goods/brands/simple/$', spu.SPUBrandView.as_view()),
    re_path(r'^meiduo_admin/goods/channel/categories/$', spu.ChannelCategorysView.as_view()),
    re_path(r'^meiduo_admin/goods/channel/categories/(?P<pk>\d+)/$', spu.ChannelCategoryView.as_view()),
    re_path(r'^meiduo_admin/goods/specs/simple/$', option.OptionSimple.as_view()),
# 权限 获取模型
    re_path(r'^meiduo_admin/permission/content_types/$', permission.ContentTypeListAPIView.as_view()),
    re_path(r'^meiduo_admin/permission/content_types/$', permission.ContentTypeAPIView.as_view()),

]
"""
默认是返回token
需求是： 不仅要返回token，还需要 user_id username

根据文档： 自定义一个方法，然后通过配置信息来加载我们的自定义方法
"""
# 1.创建router实例
router = DefaultRouter()
# 2.注册路由
router.register('^meiduo_admin/skus/images',image.ImageModelViewSet,basename='images')
#3.将router生成的路由 追加到 urlpatterns中
urlpatterns += router.urls


# urlpatterns 路由列表
# 路由匹配规则是 根据 urlpatterns中 顺序进行匹配
############SKU的路由
router.register('meiduo_admin/skus',sku.SKUModelViewSet,basename='skus')

urlpatterns += router.urls



# 作业订单管理
router.register('^meiduo_admin/orders',order.OrdersView,basename='orders')
#将router生成的路由追加到urlpatterns中
urlpatterns += router.urls

# 商品作业
# 商品规格
router.register(r'^meiduo_admin/goods/specs', specs.SpecsView, basename='spu')
urlpatterns += router.urls

#商品品牌
router.register(r'^meiduo_admin/goods/brands', brand.BrandsView, basename='brands')
urlpatterns += router.urls

#spu
router.register(r'^meiduo_admin/goods', spu.SPUGoodsView, basename='goods')
urlpatterns += router.urls

#商品选项
router.register(r'^meiduo_admin/specs/options', option.OptionsView, basename='specs')
urlpatterns += router.urls



#注册路由
router.register(r'meiduo_admin/permission/perms',permission.PermissionView,basename='perms')

#将router生成的路由追加到urlpatterns中
urlpatterns += router.urls