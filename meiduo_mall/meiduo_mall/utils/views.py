from django import http


def my_decorator(func):
    '''自定义的装饰器:判断是否登录，如果登录，执行func ，未登录，返回json'''

    # request.user表示请求的用户对象，如果是未登录用户: user 为 匿名用户，如果是登录用户: user 为 登录用户
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            # 如果用户登录, 则进入这里,正常执行
            return func(request, *args, **kwargs)
        else:
            # 如果用户未登录,则进入这里,返回400的状态码
            return http.JsonResponse({'code': 400,
                                      'errmsg': '请登录后重试'})

    return wrapper


class LoginRequiredMixin(object):
    '''自定义的Mixin扩展类'''

    # 重写的 as_view 方法
    @classmethod  # 类方法
    def as_view(cls, *args,**kwargs):
        view = super().as_view(*args,**kwargs)
        # 调用上面的装饰器进行过滤处理:
        return my_decorator(view)
