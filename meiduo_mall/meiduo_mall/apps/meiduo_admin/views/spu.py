from rest_framework.viewsets import ModelViewSet
from meiduo_admin.utils import PageNum
from meiduo_admin.serializers.spu import SPUSerializer
from goods.models import Goods
class SPUGoodsView(ModelViewSet):
    """
        SPU表的增删改查
    """
    # 指定序列化器
    serializer_class = SPUSerializer

    # 指定分页
    pagination_class = PageNum

    # 指定查询及
    def get_queryset(self):

        # 提取keyword
        keyword = self.request.query_params.get('keyword')

        if keyword == '' or keyword is None:
            return Goods.objects.all()
        else:
            return Goods.objects.filter(name__contains=keyword)


from rest_framework.generics import ListAPIView
from goods.models import Brand
from meiduo_admin.serializers.spu import BrandsSerizliser
class SPUBrandView(ListAPIView):
    """
        获取SPU表的品牌信息
    """
    serializer_class = BrandsSerizliser
    queryset = Brand.objects.all()

from goods.models import GoodsCategory
from meiduo_admin.serializers.spu import CategorysSerizliser

class ChannelCategorysView(ListAPIView):
    """
            获取spu一级分类
    """
    serializer_class = CategorysSerizliser
    queryset = GoodsCategory.objects.filter(parent=None)  # parent=None表示一级分类信息

class ChannelCategoryView(ListAPIView):
    """
        获取spu二级和三级分类
    """
    serializer_class = CategorysSerizliser  # 使用前面已经定义过的分类序列化器

    def get_queryset(self):
        pk=self.kwargs['pk']
          # 通过上级分类id 获取下级分类数据
        return GoodsCategory.objects.filter(parent=pk)
