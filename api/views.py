import importlib
import datetime
import copy

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


def get_serializer(model_class):
    class ServerSerializer(serializers.ModelSerializer):
        class Meta:
            model = model_class
            fields = "__all__"

    return ServerSerializer


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
        server_list = get_serializer(Server)(instance=server_query_set, many=True).data

        # return Response({'status': True, 'data': list(server_list)})
        return Response({'status': True, 'data': server_list})

    def post(self, request, *args, **kwargs):
        '''
        接收中控机采集到的数据
        '''
        server_info_dict = request.data
        hostname = server_info_dict['host']
        info_dict = server_info_dict['info']
        server = Server.objects.filter(hostname=hostname).first()
        if not server:
            print('服务器不存在')
            return HttpResponse('服务器不存在')
        msg_list = []
        for service_dict in settings.SERVICE_LIST:
            name = service_dict['name']
            verbose_name = service_dict['verbose_name']
            service_class = get_class(service_dict['service_class'])
            model_class = get_class(service_dict['model_class'])
            key = service_dict['key']
            data_dict = info_dict[name]['data']
            [v.update({key: k}) for k, v in data_dict.items()]
            auto_update = service_dict.get('auto_update', True)
            # 转换格式用于 serializer 数据校验
            info_list = copy.deepcopy(list(data_dict.values()))
            [item.update({'server': server.id}) for item in info_list]
            ser = get_serializer(model_class)(data=info_list, many=True)
            if ser.is_valid():
                service_obj = service_class(server, info_dict[name], verbose_name, model_class, key)

                if auto_update:
                    service_obj.auto_update()
                else:
                    service_obj.update()
                msg_list.append({'name': name, 'status': 1, 'msg': ''})
            else:
                msg_list.append({'name': name, 'status': 0, 'msg': ser.error_messages})

        server.last_update_date = datetime.date.today()
        server.save()

        return Response(msg_list)
