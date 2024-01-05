import sys
import config
import fileoperation


# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    # print("请输入一些数据并按回车键结束：")
    # for line in sys.stdin:
    #     print(line.strip())

    sra_config_obj = config.SRAData()
    config.load_all_config_data(config.SRAData)

    fo_obj = fileoperation.FileOperate(sra_config_obj.path_work, sra_config_obj.path_save,
                                       sra_config_obj.path_flag_file, sra_config_obj.list_legal_key)

    fo_obj.copy_key_log(1)

    print("结束")

# 访问 https://www.jetbrains.com/help/pycharm/ 获取 PyCharm 帮助
