SERVICE_LIST = [
    {
        'name': 'filesystem',
        'verbose_name': '文件系统',
        'service_class': 'api.service.filesystem.FileSystemService',
        'key': 'mounted',
        'model_class': 'api.models.FileSystem',
        # 'auto_update': True,
    },
    {
        'name': 'network',
        'verbose_name': '网络接口',
        'service_class': 'api.service.network.NetworkService',
        'key': 'iface_name',
        'model_class': 'api.models.Network',
    },
    {
        'name': 'memory',
        'verbose_name': '内存',
        'service_class': 'api.service.memory.MemoryService',
        'key': 'type',
        'model_class': 'api.models.Memory',
    },
]
