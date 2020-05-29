from django.contrib.auth.models import Permission
from rest_framework import serializers


class PermissionModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Permission
        fields = '__all__'


from django.contrib.auth.models import ContentType
class ContentTypeModelSerialzier(serializers.ModelSerializer):

    class Meta:
        model = ContentType
        fields = ['id','name']


from django.contrib.auth.models import Permission
from rest_framework import serializers

class PermissionSerialzier(serializers.ModelSerializer):
    """
    用户权限表序列化器
    """
    class Meta:
        model=Permission
        fields="__all__"



from rest_framework import serializers
from django.contrib.auth.models import ContentType
class ContentTypeSerialzier(serializers.ModelSerializer):
    """
    权限类型序列化器
    """
    class Meta:
        model=ContentType
        fields=('id','name')