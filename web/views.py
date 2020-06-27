from django.http import JsonResponse
from django.shortcuts import render, redirect

from api import models


class BaseResponse(object):
    def __init__(self, status=True, data=None, error=None):
        self.status = True
        self.data = data
        self.error = error

    @property
    def dict(self):
        return self.__dict__


def index(request):
    '''
    后台管理首页
    '''
    server_list = models.Server.objects.all()
    return render(request, 'index.html', {'server_list': server_list})


from django import forms


class ServerModelForm(forms.ModelForm):
    class Meta:
        model = models.Server
        fields = ['hostname', 'idc', 'cabinet_num', 'cabinet_order','status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


def create_server(request):
    '''
    新增服务器
    '''
    if request.method == 'GET':
        form = ServerModelForm()
        return render(request, 'create_server.html', {'form': form})

    form = ServerModelForm(data=request.POST)
    if form.is_valid():
        form.save()
        return redirect('/web/index/')
    return render(request, 'create_server.html', {'form': form})
