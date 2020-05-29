from rest_framework import serializers
from goods.models import Goods

class SPUSerializer(serializers.ModelSerializer):

    brand=serializers.StringRelatedField(read_only=True)
    brand_id=serializers.IntegerField()

    category1_id=serializers.IntegerField()
    category2_id=serializers.IntegerField()
    category3_id=serializers.IntegerField()

    category1 = serializers.StringRelatedField(read_only=True)
    category2 = serializers.StringRelatedField(read_only=True)
    category3 = serializers.StringRelatedField(read_only=True)

    class Meta:
        model=Goods
        fields='__all__'

from goods.models import Brand
class BrandsSerizliser(serializers.ModelSerializer):
    """
        SPU表品牌序列化器
    """
    class Meta:
        model = Brand
        fields = "__all__"

from goods.models import GoodsCategory
class CategorysSerizliser(serializers.ModelSerializer):
    """
    SPU表分类信息获取序列化器
    """

    class Meta:
        model = GoodsCategory
        fields = "__all__"
