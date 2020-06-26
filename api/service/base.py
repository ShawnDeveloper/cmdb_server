import datetime
from api.models import AssetsRecord


class BaseService(object):
    def __init__(self, server, info_dict, verbose_name, model_class, key):
        self.server = server
        self.new_data_dict = info_dict['data']
        self.verbose_name = verbose_name

        if not info_dict['status']:
            print('{}资产信息没有获取到，获取{}资产信息时出错：'.format(self.verbose_name), info_dict['error'])
            return
        self.model_class = model_class
        self.key = key

        self.db_data_list = self.model_class.objects.filter(server=self.server).all()
        try:
            self.db_data_dict = {getattr(data_obj, self.key): data_obj for data_obj in self.db_data_list}
        except AttributeError as e:
            raise RuntimeError('{} 对应的 key 可能设置错误，请检查 api.setting.py 中的配置'.format(self.__class__.__name__))
            return

        # 获取原来存在，此次提交不存在的挂载点，删除
        self.remove_set = self.db_data_dict.keys() - self.new_data_dict.keys()
        # 获取原来不存在，此次提交存在的挂载点，新增
        self.create_set = self.new_data_dict.keys() - self.db_data_dict.keys()
        # 获取原来存在，此次提交也存在的挂载点，更新
        self.update_set = self.db_data_dict.keys() & self.new_data_dict.keys()
        # 如果此次既有要删除的对象，也有要新增的对象，则直接将新增的对象数据更新到要删除的对象上
        self.reuse_dict = {}
        if self.remove_set and self.create_set:
            remove_count = len(self.remove_set)
            for i in range(0, remove_count):
                if self.create_set:
                    self.reuse_dict[self.remove_set.pop()] = self.create_set.pop()

    def update(self):
        raise NotImplementedError('{} 必须实现 update 方法'.format(self.__class__.__name__))

    def auto_update(self):
        # 重用要删除的对象
        msg_list = []
        for db_remove_key, new_create_key in self.reuse_dict.items():
            msg_list.append(
                '【删除{}】\n信息：\n{}'.format(self.verbose_name, self.get_record_msg(self.db_data_dict[db_remove_key])))
            self.update_obj(self.new_data_dict[new_create_key], self.db_data_dict[db_remove_key])
            msg_list.append(
                '【新增{}】\n信息：\n{}'.format(self.verbose_name, self.get_record_msg(self.db_data_dict[db_remove_key])))

        # 更新
        for key in self.update_set:
            old_msg = self.get_record_msg(self.db_data_dict[key])
            is_changed = self.update_obj(self.new_data_dict[key], self.db_data_dict[key])
            new_msg = self.get_record_msg(self.db_data_dict[key])

            if is_changed:
                msg_list.append('【更新{}】\n原信息：\n{}\n新信息：\n{}'.format(self.verbose_name, old_msg, new_msg))

        # 新增
        for key in self.create_set:
            obj = self.model_class.objects.create(server=self.server, **self.new_data_dict[key])
            msg_list.append('【新增{}】\n信息：\n{}'.format(self.verbose_name, self.get_record_msg(obj)))

        # 删除
        for key in self.remove_set:
            self.db_data_dict[key].delete()
            msg_list.append('【删除{}】\n信息：\n{}'.format(self.verbose_name, self.get_record_msg(self.db_data_dict[key])))

        if msg_list:
            AssetsRecord.objects.create(server=self.server, content='\n---\n'.join(msg_list))

    def get_record_msg(self, obj):
        msg_list = []
        for name, verbose_name in self.get_fields().items():
            msg_list.append('{verbose_name}：{value}'.format(verbose_name=verbose_name, value=
            '无' if not getattr(obj, name) else getattr(obj, name)))

        return '\n\t'.join(msg_list)

    # 反射更新对象信息
    def update_obj(self, dict, obj):
        is_changed = False
        for k, v in dict.items():
            if v != str(getattr(obj, k)):
                setattr(obj, k, v)
                is_changed = True

        if is_changed:
            setattr(obj, 'update_time', datetime.datetime)
            obj.save()
        return is_changed

    # 获取 model 字段对应的 verbose_name
    def get_fields(self, exclude_properties=[]):
        exclude_properties.append('server')
        exclude_properties.append('id')
        field_list = self.model_class._meta.fields
        params = [f for f in field_list if f.name not in exclude_properties]
        field_dic = {}
        for i in params:
            field_dic[i.name] = i.verbose_name
        return field_dic
