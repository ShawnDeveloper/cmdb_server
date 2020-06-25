import json
import importlib
import datetime

from django.shortcuts import HttpResponse
from django.db.models import Q

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers

from .models import *
from api import settings


def get_class(path):
    module_path, class_name = path.rsplit('.', maxsplit=1)
    module = importlib.import_module(module_path)
    cls = getattr(module, class_name)
    return cls

class ServerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Server
        fields = "__all__"


class ServerView(APIView):
    def get(self, request, *args, **kwargs):
        '''
            获取今日未采集的服务器列表
        '''

        # 今天
        today = datetime.date.today()
        # 最近汇报时间在今天之前 或 None
        '''
        # 复杂条件的构建示例
        con = Q()

        q1 = Q()
        q1.connector = 'OR'
        q1.children.append(('last_update_date__lt', today))

        q2 = Q()
        q2.connector = 'OR'
        q2.children.append(('last_update_date__isnull', True))

        con.add(q1, 'AND')
        con.add(q1, 'AND')

        server_query_set = Server.objects.filter(con).all()
        '''
        server_query_set = Server.objects.filter(
            Q(last_update_date__lt=today) | Q(last_update_date__isnull=True)).all()

        # server_list = [item[0] for item in server_query_set]
        server_list = ServerSerializer(instance=server_query_set,many=True).data

        # return Response({'status': True, 'data': list(server_list)})
        return Response({'status': True, 'data': server_list})

    def post(self, request, *args, **kwargs):
        '''
        接受中控机采集到的数据
        '''
        json_str = request.body.decode('utf8')
        server_info_dict = json.loads(json_str)
        hostname = server_info_dict['host']
        info_dict = server_info_dict['info']
        server = Server.objects.filter(hostname=hostname).first()
        if not server:
            print('服务器不存在')
            return HttpResponse('服务器不存在')

        for service_dict in settings.SERVICE_LIST:
            name = service_dict['name']
            verbose_name = service_dict['verbose_name']
            service_class = get_class(service_dict['service_class'])
            model_class = get_class(service_dict['model_class'])
            key = service_dict['key']
            auto_update = service_dict.get('auto_update', True)
            service_obj = service_class(server, info_dict[name], verbose_name, model_class, key)

            if auto_update:
                service_obj.auto_update()
            else:
                service_obj.update()

        server.last_update_date = datetime.date.today()
        server.save()

        return Response("OK")
