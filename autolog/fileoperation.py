import datetime
import json
import os
import sys
import re
import threading

import msg_queue
from common import Protocol
from log import log_info
import shutil


class FileOperate:
    path_work: str = ""
    path_save: str = ""
    path_flag_file: str = ""
    list_legal_key: list = []
    path_cur_info: str = ""
    wait_no_connect: bool = False
    allow_add_info: bool = False
    save_executing: bool = False

    def __init__(self, rv_queue, rv_path_work, rv_path_save, rv_path_flag_file, rv_list_legal_key):
        self.path_work = rv_path_work
        self.path_save = rv_path_save
        self.path_flag_file = rv_path_flag_file
        self.list_legal_key = rv_list_legal_key
        self._queue = rv_queue

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
                self.path_cur_info = full_path
        except OSError as e:
            log_info("创建文件夹失败:{0},{1}".format(full_path, str(e)))
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
                            log_info("创建文件夹失败:{0},{1}".format(full_path, str(e)))
                            return False
                        # 拷贝执行
                        at_target_path = os.path.join(full_path, at_foldername)
                        shutil.copytree(at_source_path, at_target_path)
                        self.allow_add_info = True
                        log_info("已保存日志:{0},{1}".format(at_source_path, at_target_path))
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
                            log_info(f"已删除文件夹:{at_source_path}")
                        except OSError as e:
                            log_info(f"删除文件夹{at_source_path}失败:{e}")
                            return False
        return True

    def open_work_dir(self):
        try:
            # 调用系统默认程序打开该路径
            os.startfile(self.path_work)
        except Exception as e:
            log_info("无法打开工作路径：{0},{1}".format(self.path_work, str(e)))

    def open_save_dir(self):
        try:
            # 调用系统默认程序打开该路径
            os.startfile(self.path_save)
        except Exception as e:
            log_info("无法打开保存路径：{0},{1}".format(self.path_save, str(e)))

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
                        log_info("创建文件夹失败:{0},{1}".format(full_path, str(e)))
                        return False

                    # 拷贝执行
                    at_target_path = os.path.join(full_path, at_foldername)
                    shutil.copytree(at_source_path, at_target_path)
                    log_info("已收集日志:{0},{1}".format(at_source_path, at_target_path))

                    # 删除原文件
                    try:
                        shutil.rmtree(at_source_path)
                        log_info(f"已删除文件夹:{at_source_path}")
                    except OSError as e:
                        log_info(f"删除文件夹{at_source_path}失败:{e}")
                        return False
        return True

    def _handle_response(self, rv_head, rv_content):
        if rv_head == Protocol.FO_SAVE_FILE.value:
            if not self.copy_key_log(rv_content[0]):
                self.wait_no_connect = False
                msg_queue.send_message(self._queue, "fo", "ui", Protocol.UI_SAVE_ERROR.value)
            else:
                self.wait_no_connect = True
                self.save_executing = True
        elif rv_head == Protocol.FO_DELETE_FILE.value:
            self.wait_no_connect = True
        elif rv_head == Protocol.FO_OPEN_SAVE_PATH.value:
            self.open_save_dir()
        elif rv_head == Protocol.FO_STROAGE_FILE.value:
            self.storage_log()
            msg_queue.send_message(self._queue, "fo", "ui", Protocol.UI_STROAGE_ERROR.value)
        elif rv_head == Protocol.FO_SAVE_FILE_ADD_INFO.value:
            if self.allow_add_info:
                self.add_info()
        elif rv_head == Protocol.FO_NO_CONNECT.value:
            if self.wait_no_connect():
                if self.remove_key_log():
                    if self.save_executing:
                        msg_queue.send_message(self._queue, "fo", "ui", Protocol.UI_SAVE_SUCCESS.value)
                        self.save_executing = False
                    else:
                        msg_queue.send_message(self._queue, "fo", "ui", Protocol.UI_DELETE_SUCCESS.value)
                else:
                    if self.save_executing:
                        msg_queue.send_message(self._queue, "fo", "ui", Protocol.UI_SAVE_ERROR.value)
                        self.save_executing = False
                    else:
                        msg_queue.send_message(self._queue, "fo", "ui", Protocol.UI_DELETE_ERROR.value)

    def receive_message(self):
        while True:
            message = self._queue.get()  # 从队列中获取消息
            try:
                parsed_message = json.loads(message)  # 将JSON格式的消息解析为Python字典
                # print(f"Processing message: {parsed_message}")
                if parsed_message["receiver"] == "fo":  # 检查接收方的信息是否匹配
                    # 如果匹配，处理消息或执行其他操作
                    if parsed_message["receiver"] == Protocol.FO_SAVE_FILE.value:
                        print(parsed_message["content"])
                    self._handle_response(parsed_message["head"], parsed_message["content"])
                    self._queue.task_done()
                    # print("cmd Message received by matching receiver")
                else:
                    # 如果不匹配，将消息重新入列
                    self._queue.put(message)
                    # print("Message requeued due to mismatching receiver")
            except json.JSONDecodeError:
                print("Error parsing JSON message")
                self._queue.put(message)  # 如果解析失败，将消息重新入列


def start(rv_queue, rv_path_work, rv_path_save, rv_path_flag_file, rv_list_legal_key):
    obj_fo = FileOperate(rv_queue, rv_path_work, rv_path_save, rv_path_flag_file, rv_list_legal_key)

    th_rv_msg = threading.Thread(target=obj_fo.receive_message)
    th_rv_msg.start()
    th_rv_msg.join()
