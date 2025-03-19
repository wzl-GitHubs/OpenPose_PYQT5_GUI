import sys
from collections import Counter

import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import re

# 指定字体，确保matplotlib支持中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用宋体
plt.rcParams['axes.unicode_minus'] = False  # 正确显示负号


class WorkerThread(QThread):
    finished = pyqtSignal()
    def calculate_metrics(self, data):
        """
        :data 字符串列表
        :return
        body_part_count - 身体部位的数量;
        average_score - 平均分数;
        max_count - 出现次数最多的身体部位及其计数;
        """
        body_parts = re.findall(r'BodyPart:\d+', data)  # 使用正则表达式提取身体部位和分数
        body_part_count = len(body_parts)
        scores = [float(match.group(1)) for match in re.finditer(r'score=(\d+\.\d+)', data) if match]
        average_score = sum(scores) / len(scores) if scores else 0  # 计算平均分数
        average_score_str = '%.2f' % average_score
        average_score_float = float(average_score_str)
        # 使用Counter统计每个身体部位的出现次数
        counts = Counter(body_parts)
        max_count_body_part = max(counts, key=counts.get) if counts else None
        max_count = counts[max_count_body_part] if max_count_body_part else 0
        self.finished.emit()
        # return body_part_count, float('average_score=%.2f' % average_score), max_count
        return body_part_count, average_score_float, max_count

    def start_logs(self):
        """启动线程"""
        self.start()

    def stop(self):
        self.terminate()


class MatplotlibWidget(QWidget):
    """
    雷达视图
    """
    def __init__(self, title, data: str, parent=None):

        super(MatplotlibWidget, self).__init__(parent)
        self.worker = WorkerThread()
        self.data = data
        self.title = title
        self.initUI()
        self.worker.finished.connect(self.cleanup)

    def initUI(self):
        self.fig = Figure()  # 创建一个新的matplotlib图形
        self.canvas = FigureCanvas(self.fig)  # 创建一个画布来显示图形
        self.ax = self.fig.add_subplot(111, polar=True)  # 获取图形的轴
        self.radar_map(self.data)  # 绘制雷达图
        layout = QVBoxLayout()  # 创建一个垂直布局
        layout.addWidget(self.canvas)  # 将画布添加到布局中
        self.setLayout(layout)  # 设置布局
        self.setWindowTitle(self.title)  # 设置窗口标题

    def radar_map(self, lists_data):

        body_part_count, average_score, max_count = self.worker.calculate_metrics(lists_data)
        # print(f"Body Part Count: {body_part_count}, Average Score: {average_score}, Max Count: {max_count}")
        angles = np.linspace(0, 2 * np.pi, 3, endpoint=False).tolist()  # 计算雷达图的角度
        values = [int(average_score * 100), body_part_count, max_count * 10]  # 闭合雷达图# 准备雷达图的值

        # 绘制雷达图
        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        set_color = 'red'
        if max_count == 1:
            set_color = 'red'
            set_list = [10, 17, 50, 70]
            ax.set_rticks(set_list)
        elif 1 <= max_count <= 4:
            set_color = 'blue'
            set_list = [10, 17, 50, 70]
            ax.set_rticks(set_list)
        elif max_count >= 4:
            set_color = 'red'

        self.ax.fill(angles, values, color=set_color, alpha=0.25)
        self.ax.plot(angles, values, color=set_color, linewidth=2)

        # 设置雷达图的标签
        labels = ['置信度 (%)', '关键节点数', '人数 (%10)']
        self.ax.set_xticks(angles)
        self.ax.set_xticklabels(labels)
        self.canvas.draw()  # 重新绘制画布以显示更新

    # 调用函数并打印结果
    def on_update_radar(self, keypoint_info):
        """
        更新关键节点
        :param keypoint_info: 接收的信号
        """
        self.ax.clear()
        if keypoint_info:
            keypoint_info = str(keypoint_info)
            self.radar_map(keypoint_info)

    def initThread(self):
        self.worker.start()

    def closeEvent(self, event):
        self.worker.stop()
        super(MatplotlibWidget, self).closeEvent(event)

    def cleanup(self):
        self.worker.wait()  # 等待线程安全退出
        # 执行其他清理工作


if __name__ == '__main__':
    lists_data = """
    [BodyPart:0-(0.53, 0.39) score=0.75 BodyPart:1-(0.52, 0.42) score=0.77 BodyPart:2-(0.50, 0.42) score=0.61 BodyPart:3-(0.48, 0.46) score=0.52 BodyPart:5-(0.54, 0.42) score=0.77 BodyPart:6-(0.54, 0.46) score=0.41 BodyPart:8-(0.51, 0.51) score=0.72 BodyPart:9-(0.52, 0.59) score=0.43 BodyPart:10-(0.53, 0.65) score=0.28 BodyPart:11-(0.54, 0.51) score=0.68 BodyPart:12-(0.54, 0.59) score=0.60 BodyPart:13-(0.55, 0.67) score=0.32 BodyPart:14-(0.52, 0.38) score=0.77 BodyPart:15-(0.53, 0.38) score=0.77 BodyPart:16-(0.51, 0.39) score=0.53 BodyPart:17-(0.54, 0.39) score=0.50, BodyPart:0-(0.44, 0.41) score=0.52 BodyPart:1-(0.44, 0.45) score=0.70 BodyPart:2-(0.43, 0.44) score=0.62 BodyPart:3-(0.41, 0.49) score=0.45 BodyPart:4-(0.49, 0.42) score=0.35 BodyPart:5-(0.46, 0.45) score=0.64 BodyPart:8-(0.43, 0.58) score=0.68 BodyPart:9-(0.39, 0.68) score=0.73 BodyPart:10-(0.37, 0.77) score=0.62 BodyPart:11-(0.45, 0.57) score=0.67 BodyPart:12-(0.46, 0.68) score=0.66 BodyPart:13-(0.48, 0.78) score=0.74 BodyPart:14-(0.44, 0.40) score=0.65 BodyPart:15-(0.44, 0.40) score=0.36 BodyPart:16-(0.43, 0.40) score=0.55 BodyPart:17-(0.45, 0.40) score=0.16, BodyPart:0-(0.63, 0.38) score=0.57 BodyPart:1-(0.62, 0.41) score=0.53 BodyPart:2-(0.61, 0.40) score=0.57 BodyPart:3-(0.59, 0.42) score=0.54 BodyPart:4-(0.62, 0.45) score=0.67 BodyPart:5-(0.63, 0.41) score=0.45 BodyPart:6-(0.63, 0.45) score=0.32 BodyPart:7-(0.62, 0.45) score=0.28 BodyPart:14-(0.63, 0.38) score=0.54 BodyPart:15-(0.63, 0.38) score=0.48 BodyPart:16-(0.62, 0.38) score=0.57 BodyPart:17-(0.63, 0.39) score=0.21, BodyPart:0-(0.25, 0.39) score=0.41 BodyPart:1-(0.26, 0.43) score=0.63 BodyPart:2-(0.24, 0.43) score=0.55 BodyPart:3-(0.23, 0.48) score=0.38 BodyPart:4-(0.24, 0.49) score=0.22 BodyPart:5-(0.28, 0.43) score=0.63 BodyPart:6-(0.31, 0.47) score=0.62 BodyPart:7-(0.27, 0.46) score=0.50 BodyPart:8-(0.25, 0.56) score=0.61 BodyPart:9-(0.26, 0.65) score=0.47 BodyPart:10-(0.29, 0.73) score=0.33 BodyPart:11-(0.27, 0.55) score=0.65 BodyPart:12-(0.28, 0.65) score=0.69 BodyPart:13-(0.30, 0.73) score=0.63 BodyPart:14-(0.25, 0.38) score=0.36 BodyPart:15-(0.26, 0.39) score=0.39 BodyPart:16-(0.25, 0.39) score=0.18 BodyPart:17-(0.26, 0.39) score=0.42, BodyPart:0-(0.90, 0.22) score=0.57 BodyPart:1-(0.90, 0.30) score=0.53 BodyPart:2-(0.87, 0.32) score=0.49 BodyPart:3-(0.84, 0.45) score=0.13 BodyPart:5-(0.94, 0.28) score=0.32 BodyPart:6-(0.94, 0.49) score=0.11 BodyPart:8-(0.85, 0.55) score=0.27 BodyPart:9-(0.75, 0.83) score=0.24 BodyPart:10-(0.68, 0.97) score=0.19 BodyPart:11-(0.89, 0.57) score=0.21 BodyPart:12-(0.95, 0.90) score=0.33 BodyPart:14-(0.89, 0.21) score=0.55 BodyPart:15-(0.91, 0.20) score=0.60 BodyPart:16-(0.86, 0.24) score=0.69 BodyPart:17-(0.93, 0.20) score=0.26]
    """
    lists_data0 = """
    [BodyPart:0-(0.52, 0.37) score=0.71 BodyPart:1-(0.49, 0.44) score=0.71 BodyPart:2-(0.47, 0.45) score=0.80 BodyPart:3-(0.47, 0.58) score=0.72 BodyPart:4-(0.50, 0.70) score=0.79 BodyPart:5-(0.50, 0.44) score=0.59 BodyPart:6-(0.53, 0.58) score=0.25 BodyPart:7-(0.56, 0.62) score=0.36 BodyPart:8-(0.51, 0.68) score=0.54 BodyPart:9-(0.53, 0.86) score=0.61 BodyPart:10-(0.49, 0.97) score=0.14 BodyPart:11-(0.54, 0.67) score=0.49 BodyPart:12-(0.56, 0.84) score=0.32 BodyPart:14-(0.51, 0.35) score=0.83 BodyPart:15-(0.51, 0.36) score=0.13 BodyPart:16-(0.48, 0.36) score=0.85]
    """
    lists_data = """"""
    app = QApplication(sys.argv)
    mainWin = MatplotlibWidget(data=lists_data, title="openpose")
    mainWin.show()
    sys.exit(app.exec_())
