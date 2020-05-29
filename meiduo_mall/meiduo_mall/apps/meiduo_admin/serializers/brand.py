from rest_framework import serializers
from goods.models import Brand

class BrandSerialzier(serializers.ModelSerializer):

    class Meta:
        model = Brand  # 规格选项表中的spec字段关联了规格表
        fields = "__all__"
