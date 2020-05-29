from rest_framework.viewsets import ModelViewSet
from meiduo_admin.utils import PageNum
from goods.models import GoodsSpecification
from meiduo_admin.serializers.specs import SPUSpecificationSerializer
class SpecsView(ModelViewSet):

    serializer_class = SPUSpecificationSerializer
    queryset = GoodsSpecification.objects.all()
    pagination_class = PageNum