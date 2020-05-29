from rest_framework.viewsets import ModelViewSet
from meiduo_admin.utils import PageNum
from meiduo_admin.serializers.brand import BrandSerialzier
from goods.models import Brand
from rest_framework.response import Response

class BrandsView(ModelViewSet):
    """
    品牌的增删改查
    """
    serializer_class = BrandSerialzier
    queryset = Brand.objects.all()
    pagination_class = PageNum

    def create(self, request, *args, **kwargs):
        from fdfs_client.client import Fdfs_client
        # 创建FastDFS连接对象
        client = Fdfs_client('meiduo_mall/utils/fastdfs/client.conf')
        # 获取前端传递的image文件
        data = request.FILES.get('logo')
        # 上传图片到fastDFS
        res = client.upload_by_buffer(data.read())
        # 判断是否上传成功
        if res['Status'] != 'Upload successed.':
            return Response(status=403)
        # 获取上传后的路径
        image_url = res['Remote file_id']
        # 获取sku_id
        name = request.data.get('name')
        first_letter = request.data.get('first_letter')
        # 保存图片
        brand = Brand.objects.create(name=name,
                                   logo=image_url,
                                   first_letter=first_letter)
        # 返回结果
        return Response(
            {
                'id': brand.id,
                'name': brand.name,
                'image': brand.logo.url,
                'first_letter': brand.first_letter
            },
            status=201  # 前端需要接受201状态
        )


def update(self, request, *args, **kwargs):
    # 创建FastDFS连接对象
    from fdfs_client.client import Fdfs_client
    client = Fdfs_client('meiduo_mall/utils/fastdfs/client.conf')
    # 获取前端传递的image文件
    data = request.FILES.get('logo')
    # 上传图片到fastDFS
    res = client.upload_by_buffer(data.read())
    # 判断是否上传成功
    if res['Status'] != 'Upload successed.':
        return Response(status=403)
    # 获取上传后的路径
    image_url = res['Remote file_id']
    # 查询
    brand = Brand.objects.get(id=kwargs['pk'])

    # 删除图片
    # client.delete_file(sku_image.image.name)
    # 更新图片
    brand.image = image_url
    brand.name = request.data.get('name')
    brand.first_letter = request.data.get('first_letter')
    brand.save()
    # 返回结果
    return Response(
        {
            'id': brand.id,
            'name': brand.name,
            'image': brand.logo.url,
            'first_letter': brand.first_letter
        }
    )



