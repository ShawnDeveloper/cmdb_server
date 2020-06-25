from django.db import models


class Server(models.Model):
    '''
    服务器表
    '''
    hostname = models.CharField(verbose_name='主机名', max_length=32)
    last_update_date = models.DateField(verbose_name='最近汇报时间', null=True, blank=True)


class FileSystem(models.Model):
    '''
    文件系统表
    '''
    # filesystem': 'devtmpfs', 'size': '476M', 'used': '0', 'avail': '476M', 'usage_rate': '0%', 'mounted': '/dev'
    fs = models.CharField(verbose_name='文件系统', max_length=64)
    size = models.BigIntegerField(verbose_name='大小')
    used = models.BigIntegerField(verbose_name='已使用')
    avail = models.BigIntegerField(verbose_name='可用')
    usage_rate = models.SmallIntegerField(verbose_name='使用率')
    mounted = models.CharField(verbose_name='挂载点', max_length=256)
    update_time = models.DateTimeField('更新时间', auto_now=True)
    server = models.ForeignKey(to="Server", on_delete=models.CASCADE)


class Network(models.Model):
    '''
    网络信息表
    '''
    iface_name = models.CharField(verbose_name='接口名', max_length=32)
    ip = models.CharField(verbose_name='IP 地址', max_length=32)
    netmask = models.CharField(verbose_name='子网掩码', max_length=32)
    broadcast = models.CharField(verbose_name='广播地址', max_length=32)
    update_time = models.DateTimeField('更新时间', auto_now=True)
    server = models.ForeignKey(to="Server", on_delete=models.CASCADE)


class Memory(models.Model):
    '''
    内存状态信息表
    '''
    # {'total': '972M', 'used': '206M', 'free': '75M', 'type': 'Mem', 'shared': '31M', 'buff/cache': '689M', 'available': '591M'}
    total = models.IntegerField(verbose_name='总大小')
    used = models.IntegerField(verbose_name='已使用')
    free = models.IntegerField(verbose_name='空闲')
    type = models.CharField(verbose_name='类型', max_length=32)
    shared = models.IntegerField(verbose_name='共享', null=True)
    buff_cache = models.IntegerField(verbose_name='缓冲和缓存', null=True)
    available = models.IntegerField(verbose_name='可用', null=True)
    update_time = models.DateTimeField('更新时间', auto_now=True)
    server = models.ForeignKey(to="Server", on_delete=models.CASCADE)


class Basic(models.Model):
    '''
    服务器基础信息表
    '''
    # {'type': 'basic', 'uname': 'Linux', 'version': 'CentOS Linux release 7.8.2003 (Core)', 'cpu_count': '1', 'kernel_version': '3.10.0-1127.el7.x86_64'}
    type = models.CharField(verbose_name='类型', max_length=32, default='basic')
    uname = models.CharField(verbose_name='系统类型', max_length=32)
    version = models.CharField(verbose_name='发行版', max_length=128)
    cpu_count = models.IntegerField(verbose_name='CPU个数')
    kernel_version = models.CharField(verbose_name='内核版本', max_length=128)
    update_time = models.DateTimeField('更新时间', auto_now=True)
    server = models.ForeignKey(to="Server", on_delete=models.CASCADE)


class AssetsRecord(models.Model):
    '''
    资产变更记录表
    '''
    content = models.TextField(verbose_name='变更内容')
    server = models.ForeignKey(verbose_name='服务器', to='Server', null=True, on_delete=models.SET_NULL)
    create_time = models.DateTimeField(verbose_name='时间', auto_now_add=True)
