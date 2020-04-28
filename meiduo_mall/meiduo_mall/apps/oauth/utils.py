from itsdangerous import TimedJSONWebSignatureSerializer
from django.conf import settings


def generate_access_token_by_openid(openid):
    '''把openid加密为access_token'''

    obj = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, expires_in=600)

    dict = {
        'openid': openid
    }
    # dumps 加密对象
    access_token = obj.dumps(dict).decode()

    return access_token


'''该函数的作用:
接收传入的 openid , 并将其序列化( 可以理解为加密 )为 token
解码后返回
另外这里导入的是 dev.py 文件中的 SECRET_KEY 秘钥, 为什么
导入这个呢? 主要是因为 django 创建项目成功之后, 就会给我们
生成一个秘钥, 这个秘钥就在 dev.py 文件中. itsdangerous 这个框架,
需要一个秘钥才可以正常使用, 所以需要把 dev 中的 SECRET_KEY 导入
进来.'''




# 定义函数, 检验传入的 access_token 里面是否包含有 openid
def check_access_token(access_token):
    """
    检验用户传入的 token
    :param token: token
    :return: openid or None
    """

    # 调用 itsdangerous 中的类, 生成对象
    serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, expires_in=600)
    try:
        # 尝试使用对象的 loads 函数
        # 对 access_token 进行反序列化( 类似于解密 )
        # 查看是否能够获取到数据:
        data = serializer.loads(access_token)

    except Exception as e:
        # 如果出错, 则说明 access_token 里面不是我们认可的.
        # 返回 None
        return None
    else:
        # 如果能够从中获取 data, 则把 data 中的 openid 返回
        return data.get('openid')
