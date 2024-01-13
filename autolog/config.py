import datetime
import gettext
import inspect
import os
import sys
import jsonschema
from pathlib import Path
from typing import Any, Union, get_type_hints

import orjson
from orjson import JSONDecodeError

from exceptions import TypeError
from log import log_info


CONFIG_FILE_NAME = "config.json"

USER_DATA_PREFIX = "data/user_data/"
FIXED_DATA_PREFIX = "data/fixed_data/"
os.makedirs(USER_DATA_PREFIX, exist_ok=True)

RELIC_FILE_NAME = USER_DATA_PREFIX + "relics_set.json"
LOADOUT_FILE_NAME = USER_DATA_PREFIX + "relics_loadout.json"
TEAM_FILE_NAME = USER_DATA_PREFIX + "relics_team.json"
CHAR_PANEL_FILE_NAME = USER_DATA_PREFIX + "char_panel.json"
CHAR_WEIGHT_FILE_NAME = USER_DATA_PREFIX + "char_weight.json"


def normalize_file_path(filename):
    # 尝试在当前目录下读取文件
    current_dir = os.getcwd()
    pre_file_path = os.path.join(current_dir, filename)
    if os.path.exists(pre_file_path):
        return pre_file_path
    else:
        # 如果当前目录下没有该文件，则尝试在上一级目录中查找
        parent_dir = os.path.dirname(current_dir)
        file_path = os.path.join(parent_dir, filename)
        if os.path.exists(file_path):
            return file_path
        # 如果仍然没有，则尝试在当前目录仅查找文件名
        pre_filename = str(filename).rsplit('/', 1)[-1]
        file_path = os.path.join(current_dir, pre_filename)
        if os.path.exists(file_path):
            if str(filename).rsplit('/', 1)[0] == USER_DATA_PREFIX[:-1]:
                # 判断为旧版本 (<=1.8.7) 数据文件位置
                import shutil
                shutil.move(file_path, pre_file_path)
                log.info(_("文件位置更改，由'{}'迁移至'{}'").format(pre_filename, filename))
                return pre_file_path
            return file_path
    # 如果仍然没有，则返回None
    return None


def read_json_file(filename: str, path=False, schema: dict = None) -> dict:
    """
    说明：
        读取文件
    参数：
        :param filename: 文件名称
        :param path: 是否返回路径
        :param schema: json格式规范
    """
    # 找到文件的绝对路径
    file_path = normalize_file_path(filename)
    if file_path:
        with open(file_path, "rb") as f:
            data = orjson.loads(f.read())
            if schema:
                try:
                    jsonschema.validate(data, schema)
                except jsonschema.exceptions.ValidationError as e:
                    raise Exception(_(f"JSON 数据不符合格式规范: {e}"))
            if path:
                return data, file_path
            else:
                return data
    else:
        if path:
            return {}, filename
        else:
            return {}


def modify_json_file(filename: str, key: str, value: Any) -> dict:
    """
    说明：
        将键值对写入json文件，并返回写入后的字典
    参数：
        :param filename: 文件名称
        :param key: key
        :param value: value
    返回：
        data: 修改后的json字典
    """
    # 先读，再写
    data = read_json_file(filename)
    data[key] = value
    return rewrite_json_file(filename, data)


def rewrite_json_file(filename: str, data: dict) -> dict:
    """
    说明：
        重写整个json文件
    参数：
        :param filename: 文件名称
        :param data: json的完整字典
    返回：
        data: 修改后的json字典
    """
    file_path = normalize_file_path(filename)
    if file_path is None:
        file_path = filename  # 原文件不存在，则新建
    try:
        with open(file_path, "wb") as f:
            f.write(orjson.dumps(data,
                                 option=orjson.OPT_PASSTHROUGH_DATETIME | orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_INDENT_2))
    except PermissionError as e:
        import time
        time.sleep(1)
        return rewrite_json_file(filename, data)
    return data


def get_file(path, exclude=[], exclude_file=None, get_path=False, only_place=False) -> list[str]:
    """
    获取文件夹下的文件
    """
    if exclude_file is None:
        exclude_file = []
    file_list = []
    for index, (root, dirs, files) in enumerate(os.walk(path)):
        add = True
        if (index == 0 and only_place) or not only_place:
            for i in exclude:
                if i in root:
                    add = False
            if add:
                for file in files:
                    add = True
                    for ii in exclude_file:
                        if ii in file:
                            add = False
                    if add:
                        if get_path:
                            path = root + "/" + file
                            file_list.append(path.replace("//", "/"))
                        else:
                            file_list.append(file)
    return file_list


def get_folder(path) -> list[str]:
    """
    获取文件夹下的文件夹列表
    """
    for root, dirs, files in os.walk(path):
        return dirs


language = read_json_file("config.json").get("language", "zh_CN")
if getattr(sys, 'frozen', None):
    dir = sys._MEIPASS
else:
    dir = Path()
locale_path = os.path.join(dir, "locale")
t = gettext.translation('sra', locale_path, [language])
_ = t.gettext


def add_key_value(dictionary, key, value, position):
    """
    说明:
        在指定位置添加键值对
    参数:
        :param dictionary 需要添加的字典
        :param key: 键
        :param value: 值
        :param position: 需要添加的位置
    返回:
        new_dictionary: 添加后的字典
    """
    keys = list(dictionary.keys())
    values = list(dictionary.values())
    keys.insert(position, key)
    values.insert(position, value)
    new_dictionary = dict(zip(keys, values))
    return new_dictionary


def read_maps():
    """
    说明:
        读取地图
    """
    map_list = get_file('./map', only_place=True)
    map_list_map = {}
    for map_ in map_list:
        map_data = read_json_file(f"map/{map_}")
        key1 = map_[map_.index('_') + 1:map_.index('-')]
        key2 = map_[map_.index('-') + 1:map_.index('.')]
        value = map_list_map.get(key1)
        if value is None:
            value = {}
        value[key2] = map_data["name"]
        map_list_map[key1] = value
    map_list.sort()
    log.debug(map_list)
    log.debug(map_list_map)
    return map_list, map_list_map


def insert_key(my_dict: dict, new_key, new_value, insert_after_key):
    """
    说明:
        将指定键值对插入指定key后面
    参数:
        :param my_dict: 被操作的字典
        :param new_key: 需要插入的key
        :param new_value: 需要插入的value
        :param insert_after_key: 插入到那个key后面
    """
    # 创建一个空的 OrderedDict
    new_dict = {}

    # 遍历原始字典的键值对
    for key, value in my_dict.items():
        # 将键值对添加到新的字典中
        new_dict[key] = value

        # 在指定键后面插入新的键值对
        if key == insert_after_key:
            new_dict[new_key] = new_value

    return new_dict


def get_class_methods(cls):
    """
    说明:
        获取类属性
    """
    methods = []
    for name, member in inspect.getmembers(cls):  # 获取类属性
        if not inspect.isfunction(member) and not name.startswith("__"):
            methods.append(name)
    return methods


def load_all_config_data(cls):
    methods = get_class_methods(cls)
    sradata = read_json_file(CONFIG_FILE_NAME)
    lack_methods = set(methods) - set(sradata.keys())  # 获取缺少的配置
    # 如果缺少配置则添加
    if lack_methods:
        for lack_method in lack_methods:
            sradata[lack_method] = getattr(cls, lack_method)
            modify_json_file(CONFIG_FILE_NAME, lack_method, getattr(cls, lack_method))
    # 读取配置
    for key, value in sradata.items():
        setattr(cls, key, value)


def load_config_data(cls, __name):
    """
    加载配置文件
    """
    sradata = read_json_file(CONFIG_FILE_NAME)
    if __name in sradata:
        setattr(cls, __name, sradata[__name])


class SRADataMeta(type):
    def __setattr__(cls, __name, __value):
        type_hints = get_type_hints(cls)  # 获取所有类属性的类型信息
        __name_type = type_hints.get(__name)
        if __name_type == int:
            __value = int(__value)
        elif __name_type == float:
            __value = float(__value)
        if __name_type is not None and not isinstance(__value, __name_type):
            raise TypeError(f"{__name}类型错误, 期望类型为{__name_type.__name__}, 实际类型为{type(__value).__name__}")
        modify_json_file(CONFIG_FILE_NAME, __name, __value)
        super().__setattr__(__name, __value)


class SRAData(metaclass=SRADataMeta):
    test: bool = False
    log_index: int = 0
    """日志序号"""
    path_work: str = "D:\PrintLog"
    """日志工作路径"""
    path_save: str = "D:\PrintLog"
    """日志保存路径"""
    path_flag_file: str = "D:\Work\.usual\AutoLog_V1.2\Scripts\config.txt"
    """flag控制文件路径"""
    language: str = "zh_CN"
    """语言"""
    list_legal_key: list = ["DC", 'EC']
    """关键词列表"""
    last_save: str = "2024-01-09 10:30:26"
    """上次的保存日期"""

    def __init__(self) -> None:
        ...

    def __setattr__(self, __name: str, __value: Any) -> None:
        type_hints = get_type_hints(self)  # 获取所有类属性的类型信息
        __name_type = type_hints.get(__name)
        if __name_type == int:
            __value = int(__value)
        elif __name_type == float:
            __value = float(__value)
        if not isinstance(__value, __name_type):
            raise TypeError(f"{__name}类型错误, 期望类型为{__name_type.__name__}, 实际类型为{type(__value).__name__}")
        modify_json_file(CONFIG_FILE_NAME, __name, __value)
        super().__setattr__(__name, __value)

    def __getattribute__(self, __name: str) -> Any:
        if "__" in __name:
            return super().__getattribute__(__name)
        if __name in self.__dict__:
            type_hints = get_type_hints(self)  # 获取所有类属性的类型信息
            __name_type = type_hints.get(__name)
            __value = super().__getattribute__(__name)
            if not isinstance(__value, __name_type):
                raise TypeError(
                    f"{__name}类型错误, 期望类型为{__name_type.__name__}, 实际类型为{type(__value).__name__}")
        load_config_data(SRAData, __name)
        return super().__getattribute__(__name)

    def set_config(self, key, value):
        """
        说明:
            设置配置
        """
        setattr(self, key, value)

    def get_config(self, key):
        """
        说明:
            获取配置
        """
        return getattr(self, key)

