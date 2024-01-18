import json
import os
import queue
import threading
import time
from enum import Enum

import config
import msg_queue
from common import Protocol


class Prompt(Enum):
    PROMPT_NONE = 0
    PROMPT_INPUT_ERROR = 1
    PROMPT_SAVE_SUCCESEE = 2
    PROMPT_DELETE_SUCCESEE = 3
    PROMPT_STROAGE_SUCCESEE = 4


class Ui:
    function_list: list = []
    input: int = 0
    prompt_id: Prompt = Prompt.PROMPT_NONE
    _event = threading.Event()
    index = config.config_obj.get_config("log_index")

    def __init__(self):
        self._queue = msg_queue.msgQueue
        self._event.set()
        self.function_list = [
            "功能选单：",
            "1:保存日志",
            "2:截断日志",
            "3:删除未保存日志",
            "4:保存日志并添加Info",
            "5:收纳日志",
        ]

    def show_fun_list(self):
        for function_line in self.function_list:
            print(function_line)

    def show_wait_input(self):
        self.input = 0
        line = input("请输入功能编号并按回车键结束：")
        try:
            num = int(line)  # 将输入转换为整数型
        except ValueError:  # 若无法转换成浮点型则会触发ValueError错误
            print("输入不合法！只能输入数字。")
        else:
            self.input = num



    def show_prompt(self):
        if not self._event.is_set():
            print("操作执行中，请等待")
            self._event.wait()
            self._event.clear()
        else:
            if self.prompt_id == Prompt.PROMPT_INPUT_ERROR:
                print("输入错误")

            print("当前日志序号:{0}".format(self.index))
            self.show_fun_list()

    # 定义接收消息的函数
    def receive_message(self):
        while True:
            message = self._queue.get()  # 从队列中获取消息
            try:
                parsed_message = json.loads(message)  # 将JSON格式的消息解析为Python字典
                # print(f"Processing message: {parsed_message}")
                if parsed_message["receiver"] == "ui":  # 检查接收方的信息是否匹配
                    # 如果匹配，处理消息或执行其他操作
                    if parsed_message["head"] == Protocol.UI_SAVE_SUCCESS.value:
                        self.prompt_id = Prompt.PROMPT_SAVE_SUCCESEE
                        self.index += 1
                    elif parsed_message["head"] == Protocol.UI_DELETE_SUCCESS.value:
                        self.prompt_id = Prompt.PROMPT_DELETE_SUCCESEE
                    elif parsed_message["head"] == Protocol.UI_STROAGE_SUCCESS.value:
                        self.prompt_id = Prompt.PROMPT_STROAGE_SUCCESEE
                    else:
                        self.prompt_id = Prompt.PROMPT_NONE
                        print("ui Message received by matching receiver,but illgal")

                    self._event.set()
                    self._queue.task_done()
                    print("ui Message received by matching receiver")
                else:
                    # 如果不匹配，将消息重新入列
                    self._queue.put(message)
            except json.JSONDecodeError:
                print("Error parsing JSON message")
                self._queue.put(message)  # 如果解析失败，将消息重新入列

    def send_message(self):
        if self.input == 1:
            # 保存日志
            msg_queue.send_message("ui", "cmd", Protocol.CMD_CLOSE_ALL_CLIENT.value)
            msg_queue.send_message("ui", "fo", Protocol.FO_SAVE_FILE.value, [self.index])
        elif self.input == 2:
            # 截断日志，发送消息给cmd
            msg_queue.send_message("ui", "cmd", Protocol.CMD_CLOSE_ALL_CLIENT.value)
        elif self.input == 3:
            # 删除未保存的日志
            msg_queue.send_message("ui", "cmd", Protocol.CMD_CLOSE_ALL_CLIENT.value)
            msg_queue.send_message("ui", "fo", Protocol.FO_DELETE_FILE.value)
        elif self.input == 4:
            # 保存日志且添加info
            msg_queue.send_message("ui", "cmd", Protocol.CMD_CLOSE_ALL_CLIENT.value)
            msg_queue.send_message("ui", "fo", Protocol.FO_SAVE_FILE_ADD_INFO.value)
        elif self.input == 5:
            # 收纳日志
            msg_queue.send_message("ui", "cmd", Protocol.CMD_CLOSE_ALL_CLIENT.value)
            msg_queue.send_message("ui", "fo", Protocol.FO_SAVE_FILE_ADD_INFO.value)
        self.input = 0


def start():
    obj_ui = Ui()

    th_rv_msg = threading.Thread(target=obj_ui.receive_message)
    th_rv_msg.start()

    while True:
        os.system('cls')
        obj_ui.show_prompt()
        obj_ui.show_wait_input()
        obj_ui.send_message()
