from django.http import JsonResponse
from django.shortcuts import render


def index(request):
    return render(request, 'index.html')


class BaseResponse(object):
    def __init__(self, status=True, data=None, error=None):
        self.status = True
        self.data = data
        self.error = error

    @property
    def dict(self):
        return self.__dict__


def test(request):
    res = BaseResponse()
    return JsonResponse(res.dict)
