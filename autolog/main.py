import datetime
import os
import queue
import sys
import threading
import time

import UI
import cmd
import config
import fileoperation

# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    print(datetime.datetime.today())
    t1 = threading.Thread(target=UI.start, name="th_ui")
    t1.start()

    t2 = threading.Thread(target=cmd.start, name="th_cmd")
    t2.start()

    t3 = threading.Thread(target=fileoperation.start, args=(config.config_obj.path_work,
                                                            config.config_obj.path_save,
                                                            config.config_obj.path_flag_file,
                                                            config.config_obj.list_legal_key,), name="th_cmd")
    t3.start()

    t1.join()
    t2.join()
    t3.join()

    print("main finish")
    # if sra_config_obj.last_save is None:
    #     print("请输入一个日志标号并按回车键结束：")
    #     for line in sys.stdin:
    #         try:
    #             num = int(line)  # 将输入转换为整数型
    #         except ValueError:  # 若无法转换则会触发ValueError错误
    #             print("输入不合法！只能输入数字。")
    #         else:
    #             at_log_index = num
    # else:
    #     last_date = datetime.datetime.strptime(sra_config_obj.last_save, "%Y-%m-%d")
    #     cur_date = datetime.datetime.now()
    #     if (last_date.year == cur_date.year) and (last_date.month == cur_date.month) and (
    #             last_date.day == cur_date.day):
    #         at_log_index = sra_config_obj.log_index
    #     else:
    #         at_log_index = 1
    #         sra_config_obj.set_config("log_index", at_log_index)
    #
    # at_function_lines = [
    #     "功能选单：",
    #     "1:保存日志",
    #     "2:截断日志",
    #     "3:删除未保存日志",
    #     "4:保存日志并添加Info",
    #     "5:收纳日志",
    # ]
    #
    # while True:
    #     for function_line in at_function_lines:
    #         print(function_line)
    #     line = input("请输入功能编号并按回车键结束：")
    #     try:
    #         num = int(line)  # 将输入转换为整数型
    #     except ValueError:  # 若无法转换成浮点型则会触发ValueError错误
    #         os.system('cls')
    #         print("输入不合法！只能输入数字。")
    #     else:
    #         os.system('cls')
    #         if num == 1:
    #             time.sleep(1)
    #             at_ret = fo_obj.copy_key_log(at_log_index)
    #             if at_ret:
    #                 at_log_index += 1
    #                 fo_obj.remove_key_log()
    #         elif num == 2:
    #             print("test")
    #         elif num == 3:
    #             time.sleep(1)
    #             fo_obj.remove_key_log()
    #         elif num == 4:
    #             time.sleep(1)
    #             at_ret = fo_obj.copy_key_log(at_log_index)
    #             if at_ret:
    #                 at_log_index += 1
    #                 fo_obj.remove_key_log()
    #                 fo_obj.add_info()
    #         elif num == 5:
    #             fo_obj.storage_log()
    #         else:
    #             print("输入不合法！请重新输入。")

# 访问 https://www.jetbrains.com/help/pycharm/ 获取 PyCharm 帮助
