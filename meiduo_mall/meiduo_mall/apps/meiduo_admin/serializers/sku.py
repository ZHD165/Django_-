from rest_framework import serializers
from goods.models import SKU

from goods.models import SKUSpecification
class SKUSpecificationSerializer(serializers.ModelSerializer):
    # {spec_id: "4", option_id: 8}
    # 因为前端传递过来的是 这样的数据，我们就定义 对应的字段
    spec_id = serializers.IntegerField()
    option_id = serializers.IntegerField()

    class Meta:
        model = SKUSpecification
        fields = ['spec_id','option_id']

class SKUModelSerializer(serializers.ModelSerializer):

    # 因为前端传的是 spu_id 和 category_id
    # 我们定义2个字段来接收
    spu_id = serializers.IntegerField()
    category_id=serializers.IntegerField()

    # 我们自己写字段也是没有问题的
    # 为了配合后边的更新操作
    # 因为更新操作，要获取 spu关联的模型的str  和 category关联的模型的str
    # StringRelatedField 主要是为了读取，所以我们不需要添加 required=False
    spu = serializers.StringRelatedField(required=False)
    category =serializers.StringRelatedField(required=False)

    # 因为前端传递了 specs 规格信息
    # 但是我们没有定义序列化器字段，导致了 validated_data 没有数据
    # [{spec_id: "4", option_id: 8}, {spec_id: "5", option_id: 11}]
    # 我们试着定义一个序列化器，看看它能不能帮我们实现 字段列表的保存
    specs = SKUSpecificationSerializer(many=True)

    class Meta:
        model = SKU
        fields = '__all__'
        # 设置返回SKU的所有字段
        # 对序列化器自动生成的字段进行修改
        # extra_kwargs = {
        #     'spu':{
        #         'required':False
        #     },
        #     'category':{
        #         'required':False
        #     }
        # }

    def create(self, validated_data):
        """
        1. 获取商品规格列表数据，并且从 validated_data里删除。删除的目的是剩下的validated_data数据是用于SKU保存的
        2. 先保存SKU（商品）
        3. 对商品规格列表数据进行遍历。因为我们保存 规格信息的时候 是一个一个保存的
        :param validated_data:
        :return:
        """
        # 1. 获取商品规格列表数据，并且从 validated_data里删除。删除的目的是剩下的validated_data数据是用于SKU保存的
        specs_data = validated_data.pop('specs')

        from django.db import transaction
        with transaction.atomic():
            # 创建事务回滚点
            save_id = transaction.savepoint()

            # 2. 先保存SKU（商品）
            sku = SKU.objects.create(**validated_data)
            #raise Exception('aaa') #人为异常进行模拟演示
            # 3. 对商品规格列表数据进行遍历。因为我们保存 规格信息的时候 是一个一个保存的
            #  specs: [{spec_id: "4", option_id: 8}, {spec_id: "5", option_id: 11}]
            for spec_dict in specs_data:
                # spec_dict = {spec_id: "4", option_id: 8}
                SKUSpecification.objects.create(sku=sku,**spec_dict)

            #提交事务
            transaction.savepoint_commit(save_id)

        return sku

    def update(self, instance, validated_data):

        # 我们在修改 SKU
        # instance = sku

        """
        0.获取商品规格信息
        1.先更新SKU
        2.再更新商品规格信息
        """
        # 0.获取商品规格信息
        # 为什么要pop出来。因为pop出 specs之后的数据，都和SKU相关
        specs_data = validated_data.pop('specs')
        # 1.先更新SKU
        #就是剔除一个规格再放回原来的updata更新
        # validated_data 数据当前是 只有SKU字段相关的数据
        super().update(instance,validated_data)

        # 2.再更新商品规格信息
        # 我们只允许修改 选项的值 不允许修改SPU
        from goods.models import SKUSpecification
        #  specs: [{spec_id: "4", option_id: 8}, {spec_id: "5", option_id: 11}]
        for spec_dict in specs_data:
            # spec_dict = {spec_id: "4", option_id: 8}
            # 不仅要查询商品，还需要查询商品的规格选项
            # 只能修改 option_id
            SKUSpecification.objects.filter(sku=instance,spec_id=spec_dict.get('spec_id')).update(option_id=spec_dict.get('option_id'))


        return instance

    """
    extra_kwargs = {
            'spu':{
                'required':False
            },
            'category':{
                'required':False
            }
        }
     spu = PrimaryKeyRelatedField(label='商品', queryset=Goods.objects.all(), required=False)
     category = PrimaryKeyRelatedField(label='从属类别', queryset=GoodsCategory.objects.all(), required=False)

    """

from goods.models import GoodsCategory

class GoodsCategoryModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = GoodsCategory
        fields = ['id','name']

#########2.获取SPU表名称数据 序列化器#############################################################

from goods.models import Goods
class SPUModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Goods
        fields = ['id','name']


#########3.获取SPU规格序列化器#############################################################
# 需要定义一个规格选项的序列化器
from goods.models import SpecificationOption
class SpecificationOptionModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecificationOption
        fields = ['id','value']

from goods.models import GoodsSpecification
# 规格序列化器
class GoodsSpecModelSerializer(serializers.ModelSerializer):

    # spu: str
    spu = serializers.StringRelatedField()
    # spu_id: id
    spu_id = serializers.IntegerField()

    options = SpecificationOptionModelSerializer(many=True)

    class Meta:
        model = GoodsSpecification
        fields = '__all__'















