# 这是一个示例 Python 脚本。

# 按 Shift+F10 执行或将其替换为您的代码。
# 按 双击 Shift 在所有地方搜索类、文件、工具窗口、操作和设置。
import sys
import config

# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    # print("请输入一些数据并按回车键结束：")
    # for line in sys.stdin:
    #     print(line.strip())

    sra_config_obj = config.SRAData()
    config.load_all_config_data(config.SRAData)

    print(sra_config_obj.path_crtscript)
    print("结束")

# 访问 https://www.jetbrains.com/help/pycharm/ 获取 PyCharm 帮助
