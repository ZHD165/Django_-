from _decimal import Decimal
import json
from django.utils import timezone

from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View
from django_redis import get_redis_connection

from django.db import transaction
from goods.models import SKU
from meiduo_mall.utils.views import LoginRequiredMixin
from orders.models import OrderInfo, OrderGoods
from users.models import Address


from orders.models import OrderInfo


class OrderSettlementView(LoginRequiredMixin, View):
    def get(self, request):
        '''呈现订单结算页面所需要的数据'''
        # 1.从mysql中获取address数据：address
        try:
            addresses = Address.objects.filter(user=request.user,
                                               is_deleted=False)
        except Exception as e:
            addresses = None
        # 2.遍历address，获取第一个address ===》 {}   ====》【】
        address_list = []
        for address in addresses:
            address_list.append({
                "id": address.id,
                "province": address.province.name,
                "city": address.city.name,
                "district": address.district.name,
                "place": address.place,
                "mobile": address.mobile,
                "receiver": address.receiver,
            })
        # 3.链接redis，获取redis的连接对象
        redis_conn = get_redis_connection('carts')
        user_id = request.user.id
        # 4.从redis的hash中获取count ===》 dict {}
        item_dict = redis_conn.hgetall('carts_%s' % user_id)
        # 5.从redis的set中获取sku_id  ====> dict
        selected_item = redis_conn.smembers('selected_%s' % user_id)

        dict = {}
        for sku_id in selected_item:
            dict[int(sku_id)] = int(item_dict.get(sku_id))
        # 6.获取dict的所有sku_ids ===> skus
        sku_ids = dict.keys()
        try:
            skus = SKU.objects.filter(id__in=sku_ids)
        except Exception as  e:
            return JsonResponse({'code': 400,
                                 'errmsg': '获取不到对应的商品'})
        sku_list = []
        # 7.遍历skus, 获取每一个sku  ===> {} ====> []
        for sku in skus:
            sku_list.append({
                "id": sku.id,
                "name": sku.name,
                "default_image_url": sku.default_image_url,
                "count": dict.get(sku.id),
                "price": sku.price,
            })
        # 8.拼接参数context
        context = {
            'addresses': address_list,
            'skus': sku_list,
            'freight': 10
        }
        # 9.返回json
        return JsonResponse({'code': 0,
                             'errmsg': 'ok',
                             'context': context
                             })


class OrderCommitView(View):
    """订单提交"""

    def post(self, request):
        """保存订单信息和订单商品信息"""
        # 1.  接受json参数（address_id,pay_method）

        json_dict = json.loads(request.body.decode())
        address_id = json_dict.get('address_id')
        pay_method = json_dict.get('pay_method')
        # 总体校验参数
        if not all([address_id, pay_method]):
            return JsonResponse({'code': 400,
                                 'errmsg': '缺少必传参数'})
        # 3.address_id检验
        try:
            address = Address.objects.get(id=address_id)
        except Exception as e:
            return JsonResponse({'code': 400,
                                 'errmsg': '参数address_id错误'})
        # 4.pay_method检验
        if pay_method not in [OrderInfo.PAY_METHODS_ENUM['CASH'],
                              OrderInfo.PAY_METHODS_ENUM['ALIPAY']]:
            # if pay_method not in [1,2]:    等同于上面
            return JsonResponse({'code': 400,
                                 'errmsg': '参数pay_method错误'})

        # 获取登录用户
        user = request.user
        # 生成订单编号：年月日时分秒+用户编号
        # 创建订单id
        order_id = timezone.localtime().strftime('%Y%m%d%H%M%S') + ('%09d' % user.id)
        # 显式的开启一个事务
        with transaction.atomic():
            # 创建事务保存点
            save_id = transaction.savepoint()

            # 5.往订单信息表中保存数据 保存订单基本信息
            order = OrderInfo.objects.create(
                order_id=order_id,
                user=user,
                address=address,
                total_count=0,
                total_amount=Decimal('0'),
                freight=Decimal('10.00'),
                pay_method=pay_method,
                status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'] if pay_method == OrderInfo.PAY_METHODS_ENUM['ALIPAY'] else
                OrderInfo.ORDER_STATUS_ENUM['UNSEND']
            )

            # 6.链接redis，获取redis的链接对象
            redis_conn = get_redis_connection('carts')
            # 7.从hash中获取count数据 ====> {value}
            redis_cart = redis_conn.hgetall('carts_%s' % user.id)
            # 8.从 set 中获取所有的sku_ids ===>{key}
            selected = redis_conn.smembers('selected_%s' % user.id)
            carts = {}
            for sku_id in selected:
                carts[int(sku_id)] = int(redis_cart[sku_id])
            sku_ids = carts.keys()

            # 9.获取{}中所有的sku_ids,遍历购物车中被勾选的商品信息
            for sku_id in sku_ids:
                # 增加的代码: 增加一个死循环
                while True:
                    # 10.查询SKU信息
                    sku = SKU.objects.get(id=sku_id)

                    # 增加的代码: 记录原始库存& 销量
                    origin_stock = sku.stock
                    origin_sales = sku.sales

                    # 11.判断SKU库存和销量的关系（如果库存< 销量，返回）
                    sku_count = carts[sku.id]
                    if sku_count > sku.stock:
                        # 事务回滚
                        transaction.savepoint_rollback(save_id)
                        return JsonResponse({
                            'code': 400,
                            'errmsg': '库存不足'})

                    # 模拟延迟
                    # import time
                    # time.sleep(5)

                    # 12.更改sku 的stock &sales
                    # sku.stock -= sku_count
                    # sku.sales += sku_count
                    # sku.save()

                    # 增加的代码: 乐观锁更新库存和销量
                    # 计算差值
                    new_stock = origin_stock - sku_count
                    new_sales = origin_sales + sku_count
                    result = SKU.objects.filter(id=sku_id, stock=origin_stock).update(stock=new_stock, sales=new_sales)
                    # 如果下单失败，但是库存足够时，
                    # 继续下单，直到下单成功或者库存不足为止
                    if result == 0:
                        continue

                    # 13.修改SKU销量
                    sku.goods.sales += sku_count
                    sku.goods.save()

                    # 14.保存订单商品信息 OrderGoods（多）
                    OrderGoods.objects.create(
                        order=order,
                        sku=sku,
                        count=sku_count,
                        price=sku.price,
                    )

                    # 保存商品订单中总价和总数量
                    order.total_count += sku_count
                    order.total_amount += (sku_count * sku.price)

                    # 增加的代码:
                    # 下单成功或者失败就跳出循环
                    break

                # 16.添加邮费和保存订单信息
                order.total_amount += order.freight
                order.save()
            # 清除保存点
            transaction.savepoint_commit(save_id)

        # 清除购物车中已结算的商品删除redis 中set 表对应的sku_id,hash也删掉
        pl = redis_conn.pipeline()
        pl.hdel('carts_%s' % user.id, *selected)
        pl.srem('selected_%s' % user.id, *selected)
        pl.execute()

        # 17返回响应提交订单结果
        return JsonResponse({'code': 0,
                             'errmsg': '下单成功',
                             'order_id': order.order_id
                             })


