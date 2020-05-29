from rest_framework.viewsets import ModelViewSet
from meiduo_admin.utils import PageNum
from meiduo_admin.serializers.option import OptionSerialzier
from goods.models import SpecificationOption
class OptionsView(ModelViewSet):
    """
            规格选项表的增删改查
    """
    serializer_class = OptionSerialzier
    queryset = SpecificationOption.objects.all()
    pagination_class = PageNum

from rest_framework.generics import ListAPIView
from goods.models import GoodsSpecification
from meiduo_admin.serializers.option import OptionSpecificationSerializer
class OptionSimple(ListAPIView):
    """
        获取规格信息
    """
    serializer_class = OptionSpecificationSerializer
    queryset = GoodsSpecification.objects.all()
