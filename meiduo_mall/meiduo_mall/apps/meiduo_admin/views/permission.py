""""
三个模型
"""
#用户
from django.contrib.auth.models import User
from users.models import User

# 组
from django.contrib.auth.models import Group

#权限
from django.contrib.auth.models import Permission

"""
用视图集实现 权限的增删改查
"""
from meiduo_admin.utils import PageNum
from rest_framework.viewsets import ModelViewSet
from django.contrib.auth.models import Permission
from meiduo_admin.serializers.permission import PermissionModelSerializer

class PermissionModelViewSet(ModelViewSet):

    queryset = Permission.objects.all().order_by('id')



    serializer_class = PermissionModelSerializer

    pagination_class = PageNum



# 权限类型是 对模型的权限
# 我们的权限，是表示对于模型的增删改操作
# 所以我们要把 模型查询出来
from django.contrib.auth.models import ContentType

from rest_framework.generics import ListAPIView
from meiduo_admin.serializers.permission import ContentTypeModelSerialzier

class ContentTypeListAPIView(ListAPIView):

    queryset = ContentType.objects.all()

    serializer_class = ContentTypeModelSerialzier

# 把组管理 和 管理员管理都实现才能验证权限
# 验证权限的时候 一定要注意 清除缓存



from django.contrib.auth.models import Permission
from rest_framework.viewsets import ModelViewSet
from meiduo_admin.utils import PageNum
from meiduo_admin.serializers.permission import PermissionSerialzier

class PermissionView(ModelViewSet):
    serializer_class = PermissionSerialzier
    queryset = Permission.objects.all()
    pagination_class = PageNum




from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import ContentType
from meiduo_admin.serializers.permission import ContentTypeSerialzier
class ContentTypeAPIView(APIView):

    def get(self,request):
        # 查询全选分类
        content = ContentType.objects.all()
        # 返回结果
        ser = ContentTypeSerialzier(content, many=True)

        return Response(ser.data)




from django.contrib.auth.models import Permission
from rest_framework.viewsets import ModelViewSet
from meiduo_admin.utils import PageNum
from meiduo_admin.serializers.permission import PermissionSerialzier

class PermissionView(ModelViewSet):
    serializer_class = PermissionSerialzier
    queryset = Permission.objects.all()
    pagination_class = PageNum