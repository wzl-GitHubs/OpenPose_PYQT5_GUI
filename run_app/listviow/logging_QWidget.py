import logging
import re
import sys

from PyQt5.QtGui import QTextCursor, QPalette, QFont, QTextCharFormat, QColor
from PyQt5.QtWidgets import QApplication, QWidget, QTextEdit, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import QThread, Qt, QTimer


class LogWindow(QWidget, QThread):
    """
    日志类
    """
    def __init__(self):
        super().__init__()
        self.keypoint_info = None
        self.log_text = QTextEdit(self)  # 创建一个文本编辑器用于显示日志
        self.log_text.setReadOnly(True)  # 设置为只读
        self.clear_button = QPushButton("清除日志", self)
        self.label1 = QLabel('关键节点信息')

        # 创建一个布局
        layout = QVBoxLayout(self)
        layout.addWidget(self.label1)
        self.label1.setAlignment(Qt.AlignCenter)  # 居中显示
        layout.addWidget(self.log_text)
        layout.addWidget(self.clear_button)

        # 初始化QThread和样式
        self.initThread()
        self.style_log()

        # 链接信号
        self.clear_button.clicked.connect(self.clear_logs)  # 按钮点击事件连接到清除日志的方法

    def initThread(self):
        # 这里可以初始化线程相关的操作
        # self.count_keypoint()
        pass

    def style_log(self):
        """
        设置样式
        """
        palette = QPalette()
        gray_color = QColor.fromRgb(50, 50, 50)
        palette.setColor(QPalette.Base, gray_color)  # 设置背景颜色为黑色
        self.log_text.setPalette(palette)
        font = self.log_text.font()  # 设置字体样式和颜色
        font.setFamily("Courier")
        font.setPointSize(10)
        self.log_text.setFont(font)
        self.log_text.setStyleSheet("QTextEdit { color: white; }")  # 设置字体颜色为白色

    def on_update_keypoint_End(self, keypoint_info):
        """
        更新关键节点自动滚动到底部
        :param keypoint_info: 接收的信号
        """
        if keypoint_info:
            self.keypoint_info = str(keypoint_info)
            self.log_text.append(self.keypoint_info)  # 添加到文本编辑器
            self.log_text.moveCursor(QTextCursor.End)  # 滚动到底部
            self.log_text.ensureCursorVisible()

    def calculate_metrics(self, keypoint_info):
        # 使用正则表达式找到所有的BodyPart条目
        if keypoint_info:
            body_parts = re.findall(r'BodyPar:\d+', keypoint_info)
            # 计算BodyPart个数
            body_part_count = len(body_parts)
            # 使用正则表达式找到所有的score值
            scores = [float(match.group(1)) for match in re.finditer(r'score=(\d+\.\d+)', keypoint_info) if match]
            # 计算平均分数
            average_score = sum(scores) / len(scores) if scores else 0
            logging.info(body_part_count)
            logging.info(average_score)
            return body_part_count, average_score

    def on_update_keypoint(self, keypoint_info):
        """
        更新关键节点
        :param keypoint_info: 接收的信号
        """
        if keypoint_info:
            keypoint_info = str(keypoint_info)
            self.log_text.append(keypoint_info)

    def clear_logs(self):
        """清空日志"""
        self.log_text.clear()

    def start_logs(self):
        """启动日志线程"""
        self.start()

    def stop_log(self):
        """终止线程"""
        self.deleteLater()


# 创建应用程序实例


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LogWindow()  # 创建窗口实例
    window.show()
    if app.exec_():
        window.stop_log()
        sys.exit(app.exec_())  # 运行应用程序

