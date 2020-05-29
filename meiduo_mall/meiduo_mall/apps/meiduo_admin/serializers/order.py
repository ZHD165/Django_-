from rest_framework import serializers
from orders.models import OrderInfo,OrderGoods
from goods.models import SKU

class SKUSerialzier(serializers.ModelSerializer):

    """
    商品sku表序列化器
    """
    class Meta:
        model=SKU
        fields=('name','default_image_url')

class OrderGoodsSerialziers(serializers.ModelSerializer):
    """
        订单商品序列化器
    """
    # 嵌套返回sku表数据
    sku=SKUSerialzier(read_only=True)
    class Meta:
        model=OrderGoods
        fields=('count','price','sku')

class OrderSeriazlier(serializers.ModelSerializer):
    # 关联嵌套返回 用户表数据和订单商品表数据
    user = serializers.StringRelatedField(read_only=True)
    skus = OrderGoodsSerialziers(many=True, read_only=True)

    class Meta:
        model =  OrderInfo
        fields = '__all__'