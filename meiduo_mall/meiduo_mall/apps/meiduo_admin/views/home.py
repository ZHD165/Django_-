"""
获取用户总人数
GET
count = User.objects.all().count()
retrun Response({'count':count})


"""
from django.http import JsonResponse, HttpResponseServerError
from django.views import View
from rest_framework.utils import json

from users.models import User
from rest_framework.response import Response

from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.generics import ListAPIView,RetrieveAPIView
from datetime import date
from rest_framework.permissions import IsAdminUser
class TotalCountView(APIView):

    # 添加权限
    permission_classes = [IsAdminUser]

    def get(self,request):
        today_date = date.today()
        count = User.objects.all().count()
        return Response({'count': count,'date':today_date})

# GenericAPIView 一般要设置 序列化器 和 查询结果集
# 和 mixin 配合使用 最简单
# 我们这里是不需要设置 查询结果集和序列化器的 因为get方法我们实现了 没有调用响应方法
# class TotalCountGenericAPIView(GenericAPIView):
#     def get(self, request):
#         count = User.objects.all().count()
#         return Response({'count': count})

# class TotalCountListAPIView(ListAPIView):
#
#     def get(self,request):
#         count = User.objects.all().count()
#         return Response({'count': count})

"""
日活跃用户统计

最后的登录时间
查询用户最后登录的时间是今天的 数量
"""
class UserDayActiveAPIView(APIView):

    def get(self,request):
        today=date.today()
        # gte 大于等于
        #           datetime
        # today     date
        # last_login__gte=today 比对 date
        count = User.objects.filter(last_login__gte=today).count()

        return Response({'count':count})

"""
日下单用户量统计

User 和 订单 的关系
1个用户 可以下 很多订单
1：n 

关联模型类名小写__属性名__条件运算符=值
BookInfo.objects.filter(heroinfo__hcomment__contains='八')


日下单用户量
用户量  User.objects.filter(orderinfo__create_time__gte=today).count()

"""

class UserOrderInfoCountAPIView(APIView):

    def get(self,request):
        today = date.today()
        count = User.objects.filter(orderinfo__create_time__gte=today).count()
        return Response({'count':count})

"""
[
    {
        "count": "用户量",
        "date": "日期"
    },
    {
        "count": "用户量",
        "date": "日期"
    },
    ...
]
获取当天的日期
获取30天前的日期
初始化一个列表
遍历获取30天的用户增量 
    获取某一天的日期
    获取某一天的用户增量
"""
from datetime import timedelta
class MonthUserView(APIView):

    def get(self,request):
        # 获取当天的日期
        today=date.today()
        # 获取30天前的日期
        start_date = today - timedelta(days=30)
        # 初始化一个列表
        data_list = []
        # 遍历获取30天的用户增量
        for i in range(31):
            #     获取某一天的日期
            # 从30天前，往后来获取数据
            index_date=start_date + timedelta(days=i)
            pause_date=start_date + timedelta(days=(i+1))
            #  获取某一天的用户增量
            # index_date 日期类型
            # 2020-5-20
            # 2020-5-20 10:00:00
            # 2020-5-20 00:00:00  ～ 2020-5-21 00：00:00
            # date_joined = models.DateTimeField
            # 过滤条件是： 大于等于当天
            #            小于后一天
            # date_joined 加入时间（注册时间）
            count = User.objects.filter(date_joined__gte=index_date,
                                        date_joined__lt=pause_date).count()

            data_list.append({
                'date':index_date,
                'count':count
            })

        return Response(data_list)

class DayUserView(APIView):
    def get(self,request):
        today = date.today()
        count = User.objects.filter(date_joined__gte=today).count()

        return Response({
            'count':count,
            'date':today
            })


# class CategoryProductVisitsView(APIView):
#     def post(self,request):
#         data = json.loads(request.body.decode())
from django import http
# from goods.models import GoodsVisitCount, GoodsCategory
#
#
# class DetailVisitView(View):
#     """详情页分类商品访问量"""
#
#     def post(self, request, category_id):
#         """记录分类商品访问量"""
#         try:
#             category = GoodsCategory.objects.get(id=category_id)
#         except GoodsCategory.DoesNotExist:
#             return JsonResponse({'code':400,
#                                  'errmsg':'缺少必传参数'})
#
#         # 获取今天的日期
#         from django.utils import timezone
#         today_date=timezone.localdate()
#         try:
#             # 查询今天该类别的商品的访问量
#             counts_data = category.goodsvisitcount_set.get(date=today_date)
#         except GoodsVisitCount.DoesNotExist:
#             # 如果该类别的商品在今天没有过访问记录，就新建一个访问记录
#             counts_data = GoodsVisitCount()
#
#         try:
#             counts_data.category = category
#             counts_data.count += 1
#             counts_data.save()
#         except Exception as e:
#             return HttpResponseServerError('服务器异常')
#
#         return JsonResponse({'code': 0, 'errmsg': 'OK'})


from goods.models import GoodsVisitCount
from meiduo_admin.serializers.home import UserCategoryCountSerializer
class UserCategoryCountAPIView(APIView):

    def get(self,request):

        #获取当天日期
        today=date.today()

        #查询数据
        data = GoodsVisitCount.objects.filter(date__gte=today)

        serializer = UserCategoryCountSerializer(data,many=True)

        return Response(serializer.data)