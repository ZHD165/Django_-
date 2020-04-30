from django.http import JsonResponse
from django.shortcuts import render
# django 框架自带函数
from django.core.cache import cache
from django.views import View
from .models import Area


# Create your views here.
class ProvinceAreasView(View):
    """省级地区"""

    def get(self, request):
        """提供省级地区数据
        1.查询省级数据
        2.序列化省级数据
        3.响应省级数据
        4.补充缓存逻辑
        """
        list = cache.get("province")
        if not list:
            try:
                # 1.查询省级数据
                province_model_list = Area.objects.filter(parent__isnull=True)

                # 2.整理省级数据
                list = []
                for province in province_model_list:
                    list.append({
                        'id': province.id,
                        'name': province.name
                    })

                cache.set('province', list, 3600)

            except Exception as e:
                # 如果报错, 则返回错误原因:
                return JsonResponse({'code': 400,
                                     'errmsg': '省份数据错误'})

        # 3.返回整理好的省级数据
        return JsonResponse({'code': 0,
                             'errmsg': 'OK',
                             'province_list': list})


'''class SubAreasView(View):
    """子级地区：市和区县"""

    def get(self, request, pk):
        """提供市或区地区数据
        1.查询市或区数据
        2.序列化市或区数据
        3.响应市或区数据
        4.补充缓存数据
        """

        try:
            # 1.查询市或区数据
            sub_model_list = Area.objects.filter(parent=pk)
            #  查询省份数据
            parent_model = Area.objects.get(id=pk)

            # 2.整理市或区数据
            sub_list = []
            for sub_model in sub_model_list:
                sub_list.append({'id': sub_model.id,
                                 'name': sub_model.name})

            sub_data = {
                'id': parent_model.id,  # pk
                'name': parent_model.name,
                'subs': sub_list
            }

        except Exception as e:
            return http.JsonResponse({'code': 400,
                                      'errmsg': '城市或区县数据错误'})

        # 3.响应市或区数据 ok: 0
        return http.JsonResponse({'code': 0,
                                  'errmsg': 'OK',
                                  'sub_data': sub_data})
                                  '''

'''增加缓存的子级地区'''


class SubAreasView(View):
    """子级地区：市和区县"""

    def get(self, request, pk):

        '''接受pk值，通过pk值，获取对应的对象，还要获取pk对应的下一级的对象'''
        '''提供市或区地区数据
        1.查询市或区数据
        2.序列化市或区数据
        3.响应市或区数据
        4.补充缓存数据
        '''
        # 判断是否有缓存
        dict = cache.get('sub_data_%s' % pk)

        if not dict:

            # 1.查询市或区数据
            try:
                province = Area.objects.get(id=pk)
                # 1.获取pk对相应的下一级所以偶的数据对象
                sub_model_list = Area.objects.filter(parent=pk)
                # 2.更具pk查询市或区的父级



                list = []
                # 3.便利下一级所有数据对象，获取每一个
                for sub_model in sub_model_list:
                    # 4. 把每一个对象 ===> {}===>[]
                    list.append({
                        'id': sub_model.id,
                        'name': sub_model.name
                    })

                # 5.创建一个dict，badict整理好
                dict = {
                    'id': province.id,  # pk
                    'name': province.name,
                    'subs': list
                }

                # 增加，缓存省级数据
                cache.set('sub_data_' + pk, dict, 3600)

            except Exception as e:
                return JsonResponse({'code': 400,
                                     'errmsg': '获取不到数据'})

        # 6.返回json数据
        return JsonResponse({'code': 0,
                             'errmsg': 'OK',
                             'sub_data': dict})




