from rest_framework.viewsets import ModelViewSet
from goods.models import SKU
from meiduo_admin.serializers.sku import SKUModelSerializer
from meiduo_admin.utils import PageNum


class SKUModelViewSet(ModelViewSet):
    queryset = SKU.objects.all()

    serializer_class = SKUModelSerializer

    # sku数据是要求必须分页的
    pagination_class = PageNum


#########SKU的保存################################################
"""
见招拆招
遇到什么问题，解决什么问题
SKU = Stock Keeping Unit （库存量单位）            具体一个商品
SPU = Standard Product Unit （标准产品单位）        1类商品

1. 序列化器很关键
SKUModelSerializer():

    spu = PrimaryKeyRelatedField(label='商品', queryset=Goods.objects.all())
    category = PrimaryKeyRelatedField(label='从属类别', queryset=GoodsCategory.objects.all())


请求方式： POST  meiduo_admin/skus/

请求参数： 通过请求头传递jwt token数据。
spu_id		    商品SPU ID
category_id		三级分类

问题1： 前端传递的2个数据 spu_id 和 category_id  与 我们的 SKUSerializer 自动生成的字段 不匹配

解决方案：
    在序列化器中 我们自己写2个字段， spu_id=IntegerFiled 和category_id=IntegerFiled



问题2：
SKUModelSerializer():
    spu_id = IntegerField()
    category_id = IntegerField()
    spu = PrimaryKeyRelatedField(label='商品', queryset=Goods.objects.all())
    category = PrimaryKeyRelatedField(label='从属类别', queryset=GoodsCategory.objects.all())

required	表明该字段在反序列化时必须输入，默认True

问题自动生成的序列化器，要求传入spu 和 category 
前端没有传 spu和category 前端传递的是 spu_id 和 category_id

解决方法是： 改为不必须传入


问题3： 当我们新增了一个SKU之后，它的规格选项 也应该 确定了，也应该保存起来
实际并没有保存

为什么没有保存？

前端传递了 规格信息 一下就是规格信息
specs: [{spec_id: "4", option_id: 8}, {spec_id: "5", option_id: 11}]


序列化器的 validated_data 里没有规格信息
为什么呢？
因为序列化器中没有定义 specs 的字段来接收数据

我们在进行反序列化的时候 ，应该让我们传递的数据 和 序列化器字段有一个 一一对应关系


问题4：
The `.create()` method does not support writable nested fields by default.
The `.update()` method does not support writable nested fields by default


Writable nested serializers
By default nested serializers are read-only. 
If you want to support write-operations to a nested serializer field 
you'll need to create create() and/or update() methods 
in order to explicitly specify how the child relationships should be saved.


SKU         商品表(1)
SKUSp       商品规格表（n）

默认我们的序列化器 是不支持 列表字典的保存的
如果想要实现，自己重写 序列化器的 crate方法


1. 先保存sku
2. 遍历保存商品规格信息

def create(self, validated_data):
        # 获取商品规格信息，并从 validated_data 删除商品规格信息。 因为 sku不需要商品规格信息
        tracks_data = validated_data.pop('tracks')
        # 先保存sku
        album = Album.objects.create(**validated_data)

        # 遍历保存商品规格信息  specs: [{spec_id: "4", option_id: 8}, {spec_id: "5", option_id: 11}]
        for track_data in tracks_data:
            Track.objects.create(album=album, **track_data)

        return album



def create(self, validated_data):
        # 获取商品规格信息，并从 validated_data 删除商品规格信息。 因为 sku不需要商品规格信息
        specs_data = validated_data.pop('specs')
        # 先保存sku
        sku = SKU.objects.create(**validated_data)

        # 遍历保存商品规格信息  specs: [{spec_id: "4", option_id: 8}, {spec_id: "5", option_id: 11}]
        for spec_dict in specs_data:
            # spec_dict = {spec_id: "4", option_id: 8}
            SKUOptionfication.objects.create(sku=sku, **spec_dict)

        return sku

"""

"""
新增SKU我们要实现的大的步骤
1、获取三级分类信息
    parent_id = None        是一级分类   （1~37）
    parent_id = (1,37)      是二级分类   （38~114）
    parent_id = (38,114)    是三级分类   （114,～）

    获取三级分类， parent_id >= 38

2、获取SPU表名称数据
    获取所有的SPU数据
3、获取SPU商品规格信息
4、保存SKU数据
"""

"""
# GoodsCategory.objects.filter(parent=None) #一级分类数据
# GoodsCategory.objects.filter(parent_id__gte=1,parent_id__lte=37) #二级分类
# GoodsCategory.objects.filter(parent_id__gte=38) #三级分类

# GoodsCategory.objects.filter(parent=None) #一级分类数据

# 三级分类
cat = GoodsCategory.objects.get(id=115)
# 三级分类下边 就没有四级分类了
# 查询
cat.goodscategory_set.all()
# None 0

# 关联过滤查询
#关联模型类名小写__属性名__条件运算符=值
# count 不是本类的一个属性
# 所以我们再过滤的时候，查询 没有四级分类的数据，就是三级分类

# 关联过滤查询
#关联模型类名小写__属性名__条件运算符=值
# GoodsCategory 关联着 GoodsCategory
# GoodsCategory.objects.filter(GoodsCategory=None)
GoodsCategory.objects.filter(goodscategory=None)

1. GoodsCategory 关联着 GoodsCategory (自己关联自己)
 GoodsCategory.objects.filter(GoodsCategory=None)
 关联过滤查询
 关联模型类名小写__属性名__条件运算符=值
 GoodsCategory.objects.filter(goodscategory=)

2. 一级下边有二级
二级下边有三级
三级下边有None

GoodsCategory.objects.filter(goodscategory=None)

"""

from goods.models import GoodsCategory
from rest_framework.views import APIView
from meiduo_admin.serializers.sku import GoodsCategoryModelSerializer
from rest_framework.response import Response


# 获取三级分类数据
class CategoryAPIView(APIView):

    def get(self, request):
        """
        1.获取所有三级分类数据
        2.将对象列表转换为字典列表
        3.返回响应
        :param request:
        :return:
        """
        # 1.获取所有三级分类数据
        cats = GoodsCategory.objects.filter(goodscategory=None)
        # 2.将对象列表转换为字典列表
        serializer = GoodsCategoryModelSerializer(cats, many=True)
        # 3.返回响应
        return Response(serializer.data)


#########2.获取SPU表名称数据#############################################################

from goods.models import Goods
from rest_framework.generics import ListAPIView
from meiduo_admin.serializers.sku import SPUModelSerializer


class SPUListAPIView(ListAPIView):
    queryset = Goods.objects.all()

    serializer_class = SPUModelSerializer


#####3.获取SPU商品规格信息###############################################
"""
spu_id  --> 规格      -->     规格选项

iPhone8     颜色              金色，灰色，蓝色
            内存              64G,128G

tb_spu --> tb_goods_specification --> tb_specification_option

spu_id=2 
iPhone8

1.先假设 spu_id 就是2. 我们就根据spu_id=2 查询规格

"""
# 1.假设id=2
# spu_id = 2

from goods.models import GoodsSpecification
from meiduo_admin.serializers.sku import GoodsSpecModelSerializer


# 2.查询规格
# gs = GoodsSpecification.objects.filter(spu_id=spu_id)
# [<GoodsSpecification: Apple iPhone 8 Plus: 颜色>, <GoodsSpecification: Apple iPhone 8 Plus: 内存>]
# gs 是一个对象列表，对象列表肯定要创建一个序列化器

# gs = GoodsSpecification.objects.filter(spu_id=2)[0].options

class GoodsSpecAPIView(APIView):

    def get(self, request, pk):
        gs = GoodsSpecification.objects.filter(spu_id=pk)

        serializer = GoodsSpecModelSerializer(gs, many=True)

        return Response(serializer.data)



