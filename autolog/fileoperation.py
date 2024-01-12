import datetime
import os
import sys
import re
from log import log
import shutil


class FileOperate:
    path_work: str = ""
    path_save: str = ""
    path_flag_file: str = ""
    list_legal_key: list = []

    path_cur_info: str = ""

    def __init__(self, rv_path_work, rv_path_save, rv_path_flag_file, rv_list_legal_key):
        self.path_work = rv_path_work
        self.path_save = rv_path_save
        self.path_flag_file = rv_path_flag_file
        self.list_legal_key = rv_list_legal_key

    def judge_folder_key_exist(self):
        for at_foldername in os.listdir(self.path_work):
            if os.path.isdir(os.path.join(self.path_work, at_foldername)):
                for key in self.list_legal_key:
                    re_result = re.search(key, at_foldername)
                    if re_result:
                        return True
        return False

    def copy_key_log(self, rv_index):
        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        folder_name = '{0}No.{1}'.format(now, rv_index)

        full_path = os.path.join(self.path_save, folder_name)
        try:
            # 如果文件夹不存在则创建新的文件夹
            if not os.path.exists(full_path):
                os.makedirs(full_path)
                self.path_info = full_path
        except OSError as e:
            log.info("创建文件夹失败:{0},{1}".format(full_path, str(e)))
            return False

        for at_foldername in os.listdir(self.path_work):
            at_source_path = os.path.join(self.path_work, at_foldername)
            if os.path.isdir(at_source_path):
                for key in self.list_legal_key:
                    re_result = re.search(key, at_foldername)
                    if re_result:  # 关键词存在
                        # 检查同名文件夹
                        full_path = os.path.join(full_path, key)
                        try:
                            # 如果文件夹不存在则创建新的文件夹
                            if not os.path.exists(full_path):
                                os.makedirs(full_path)
                        except OSError as e:
                            log.info("创建文件夹失败:{0},{1}".format(full_path, str(e)))
                            return False
                        # 拷贝执行
                        at_target_path = os.path.join(full_path, at_foldername)
                        shutil.copytree(at_source_path, at_target_path)
                        log.info("已保存日志:{0},{1}".format(at_source_path, at_target_path))
        return True

    def remove_key_log(self):
        for at_foldername in os.listdir(self.path_work):
            at_source_path = os.path.join(self.path_work, at_foldername)
            if os.path.isdir(at_source_path):
                for key in self.list_legal_key:
                    re_result = re.search(key, at_foldername)
                    if re_result:  # 关键词存在
                        try:
                            shutil.rmtree(at_source_path)
                            log.info(f"已删除文件夹:{at_source_path}")
                        except OSError as e:
                            log.info(f"删除文件夹{at_source_path}失败:{e}")
                            return False
        return True

    def open_work_dir(self):
        try:
            # 调用系统默认程序打开该路径
            os.startfile(self.path_work)
        except Exception as e:
            log.info("无法打开工作路径：{0},{1}".format(self.path_work, str(e)))

    def open_save_dir(self):
        try:
            # 调用系统默认程序打开该路径
            os.startfile(self.path_save)
        except Exception as e:
            log.info("无法打开保存路径：{0},{1}".format(self.path_save, str(e)))

    def add_info(self):
        at_path_info_file = os.path.join(self.path_info, "info.csv")
        with open(at_path_info_file, "w") as file:
            pass

    def storage_log(self):
        for at_foldername in os.listdir(self.path_save):
            at_source_path = os.path.join(self.path_save, at_foldername)
            if os.path.isdir(at_source_path):
                if "_" in at_foldername:
                    at_result = at_foldername.split("_")[0]
                    at_date_obj = datetime.datetime.strptime(at_result, "%Y%m%d")
                    foldername = at_date_obj.strftime("%Y年%m月%d日")
                    # 检查同名文件夹
                    full_path = os.path.join(self.path_save, foldername)
                    try:
                        # 如果文件夹不存在则创建新的文件夹
                        if not os.path.exists(full_path):
                            os.makedirs(full_path)
                    except OSError as e:
                        log.info("创建文件夹失败:{0},{1}".format(full_path, str(e)))
                        return False

                    # 拷贝执行
                    at_target_path = os.path.join(full_path, at_foldername)
                    shutil.copytree(at_source_path, at_target_path)
                    log.info("已收集日志:{0},{1}".format(at_source_path, at_target_path))

                    # 删除原文件
                    try:
                        shutil.rmtree(at_source_path)
                        log.info(f"已删除文件夹:{at_source_path}")
                    except OSError as e:
                        log.info(f"删除文件夹{at_source_path}失败:{e}")
                        return False
        return True
