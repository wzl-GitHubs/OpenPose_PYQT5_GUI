import glob
import os
import sys
from pathlib import Path

app_script_path = Path(__file__).resolve()  # 获取当前脚本文件（app.py）的绝对路径

project_root_path = app_script_path.parent.parent  # 获取 run_app 目录的父目录路径（即项目根目录）
sys.path.append(str(project_root_path))

from PyQt5 import QtWidgets
from run_app.main_ui import Ui_MainWindow

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(window)
    window.show()
    # 启动事件循环
    app.exec_()
    temp_folder = r'C:/Windows/Temp/'
    json_files_pattern = os.path.join(temp_folder, '*.json')

    # 使用glob.glob找到所有匹配的文件
    json_files = glob.glob(json_files_pattern)

    # 遍历找到的文件并逐一删除
    for json_file in json_files:
        os.remove(json_file)
        print(f"Deleted file: {json_file}")
