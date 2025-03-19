import ctypes
import mediapipe as mp
import os
import argparse
import sys
import time
from typing import Tuple
import cv2
from PyQt5.QtCore import pyqtSignal, QTimer, Qt
from PyQt5.QtGui import QPixmap, QImage, QGuiApplication
import logging
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QWidget, QGridLayout
from tf_pose.estimator import TfPoseEstimator, logger
from tf_pose.networks import model_wh, get_graph_path
from threading import Lock
from run_app.worker.worker import Worker
# from mp_pose.posenet_worker_video import Worker_video as posenet


class Worker_video(Worker):
    """
    摄像头
    """
    image_processed = pyqtSignal(QPixmap)  # 用于发送处理后的图像
    stopSignal = pyqtSignal()  # 用于停止线程
    loggerSignal = pyqtSignal(list)

    def __init__(self, WorkerName=None, FilePath=None):
        super(Worker_video, self).__init__()

        self.is_DualSwitch = 'openpose'
        # self.posenet = posenet(FilePath=FilePath)
        self.DualSwitch = None
        self.is_open = None
        self.is_open_models = 'openpose'
        self.humans = None
        self.image = None
        self.lock = Lock()  # 创建一个锁对象
        self.is_paused = False  # 用于标记线程是否被暂停
        self.fps_time = time.time()
        self.WorkerName = WorkerName
        self.FilePath = FilePath
        self.logger = logging.getLogger(__name__)
        self.root_dir = os.path.split(os.path.abspath(__file__))[0]
        self.args = self.parse_arguments()
        # self.video_cap = cv2.VideoCapture(self.args.video)
        self.video_cap = cv2.VideoCapture(self.FilePath)
        self.total_frames = int(self.video_cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = self.video_cap.get(cv2.CAP_PROP_FPS)
        self.frame = 0
        self.w, self.h = model_wh(self.args.resolution)
        if self.w > 0 and self.h > 0:
            self.e = TfPoseEstimator(get_graph_path(self.args.model), target_size=(self.w, self.h))
        else:
            self.e = TfPoseEstimator(get_graph_path(self.args.model), target_size=(432, 368))

        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose
        self.pose_model = self.init_pose_model()

        # 创建定时器转发姿态估计日志
        self.keypoint_timer = QTimer(self)
        self.keypoint_timer.timeout.connect(self.on_signal_list)
        self.keypoint_timer.start(1000)  # 设置定时器触发间隔为1000毫秒（1秒）

        self.stop_label_icon = QPixmap('../../resources/icon/werker_stop.png')

    def init_pose_model(self):
        """初始化MediaPipe姿态估计模型"""
        model_complexity = 1
        enable_segmentation = False
        min_detection_confidence = 0.5
        min_tracking_confidence = 0.5

        return self.mp_pose.Pose(
            model_complexity=model_complexity,
            enable_segmentation=enable_segmentation,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )

    def parse_arguments(self, **kwargs):
        """
        参数解析
        :param **kwargs:
        :return:
        """
        parser = argparse.ArgumentParser(description='tf-pose-estimation Video')
        parser.add_argument('--video', type=str, default=self.FilePath)
        parser.add_argument('--resolution', type=str, default='432x368',
                            help='network input resolution. default=432x368')
        # parser.add_argument('--model', type=str, default='mobilenet_thin',
        #                       help='cmu / cmu_freeze/ cmu_graph
        #                       mobilenet_thin/ mobilenet_thin_freeze/ mobilenet_thin_graph
        #                       pose_lightweight')
        parser.add_argument('--model', type=str, default='mobilenet_thin',
                            help='cmu / mobilenet_thin/ pose_lightweight')

        parser.add_argument('--show-process', type=bool, default=False,
                            help='for debug purpose, if enabled, speed for inference is dropped.')
        parser.add_argument('--showBG', type=bool, default=True, help='False to show skeleton only.')
        parser.add_argument('--output_json', type=str, default='C:/Windows/Temp/', help='writing output json dir')
        parser.add_argument('--resize-out-ratio', type=float, default=4.0,
                            help='if provided, resize heatmaps before they are post-processed. default=1.0')
        # h.解析命令行参数
        return parser.parse_args()

    def InitialEnvironment(self, WorkerName=None, FilePath=None) -> None:
        """
        环境初始化
        """
        try:
            if self.video_cap is None:
                self.deleteLater()
                Worker_video(WorkerName, FilePath)
                self.video_cap = cv2.VideoCapture(self.args.video)
                if not self.video_cap.isOpened():
                    raise Exception("Failed to open video")
                logger.info("Camera initialized successfully")
        except cv2.error as e:
            logger.error(f"Error initializing video: {e}")
            print(f"Error initializing video: {e}")  # 打印到控制台
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            print(f"An unexpected error occurred: {e}")  # 打印到控制台

    def run(self):
        self.run_models()

    def run_models(self) -> None:
        """
        主运算逻辑
        """
        while self.is_paused:
            with self.lock:
                ret, self.image = self.video_cap.read()
                if ret:
                    if self.is_open_models:
                        # self.is_DualSwitch = 'openpose'
                        if self.is_DualSwitch == 'openpose':
                            self.humans = self.e.inference(self.image, resize_to_default=(self.w > 0 and self.h > 0),
                                                           upsample_size=self.args.resize_out_ratio)
                            self.image = TfPoseEstimator.draw_humans(self.image, self.humans, imgcopy=False,
                                                                     frame=self.frame)
                                                                     # output_json_dir=self.args.output_json)
                        elif self.is_DualSwitch == 'posenet':
                            results = self.pose_model.process(self.image)
                            if results.pose_landmarks:
                                self.mp_drawing.draw_landmarks(
                                    self.image,
                                    results.pose_landmarks,
                                    self.mp_pose.POSE_CONNECTIONS,
                                    connection_drawing_spec=self.mp_drawing.DrawingSpec(
                                        color=(0, 255, 0), thickness=2))
                                time.sleep(0.005)  # 睡眠33毫秒
                                self.humans = ['现在运行的是Google的posenet']
                    else:
                        time.sleep(0.029)  # 睡眠33毫秒
                        self.humans = ['现在运行的是opencv读取的原视频']
                        pass

                    self.frame += 1
                    fps = (1.0 / (time.time() - self.fps_time))
                    plan = (self.frame / self.total_frames) * 100
                    total_time = self.video_cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
                    len_time = self.total_frames // self.fps

                    self.txt_fond("FPS_Former", fps, pose=4)
                    self.txt_fond("Timel_Long", len_time, pose=6)
                    self.txt_fond("FPS_Real   ", self.fps, pose=2)
                    self.txt_fond("Time_Real ", total_time, pose=8)
                    self.txt_fond("Plan       ", plan, pose=10)

                    self.fps_time = time.time()
                    height, width, channels = self.image.shape
                    bytes_per_line = channels * width
                    # cv2.imshow('test', self.image)
                    rgb_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
                    qimage = QImage(rgb_image.data, width, height, bytes_per_line, QImage.Format_RGB888)
                    pixmap = QPixmap.fromImage(qimage)
                    self.image_processed.emit(pixmap)

                elif not ret:
                    self.InitialEnvironment()
                    self.is_open = True
                    self.frame = 0
                    self.image_processed.emit(self.stop_label_icon)
                    self.lock.locked()
                # else:
                #     self.image_processed.emit(self.stop_label_icon)
                #     self.lock.release()  # 注意：这里释放锁可能会导致线程退出循环
                #     time.sleep(0.1)  # 等待一小段时间再次检查锁状态
                #     continue
        else:
            self.lock.locked()
            # self.image_processed.emit(self.stop_label_icon)

    def txt_fond(self, txt_str: str, input_str: object, pose: int = 1, font: int = cv2.FONT_HERSHEY_COMPLEX_SMALL,
                 colour: Tuple[int, int, int] = (255, 0, 0), font_thickness: int = 2) -> None:
        """
        opencv 图像文本显示

        :param txt_str: 文本标题
        :param input_str: 文本内容
        :param pose: 文本位置，取值范围（1,20)
        :param colour: 文字rgb颜色，取值范围(0.0.0)~(255.255.255)
        :param font_thickness: 字体粗细:1 正常； 2 加粗
        :param font: 字体样式
                cv2.FONT_HERSHEY_SIMPLEX：基础字体
                cv2.FONT_HERSHEY_PLAIN：没有斜体或粗体的简单字体。
                cv2.FONT_HERSHEY_DUPLEX：比FONT_HERSHEY_PLAIN稍微复杂一些的字体。
                cv2.FONT_HERSHEY_COMPLEX：具有更多字符和符号的复杂字体。
                cv2.FONT_HERSHEY_TRIPLEX：具有更多风格和字符的三重字体。
                cv2.FONT_HERSHEY_COMPLEX_SMALL：FONT_HERSHEY_COMPLEX的小型版本。
                cv2.FONT_HERSHEY_SCRIPT_SIMPLEX：手写风格的字体。
                cv2.FONT_HERSHEY_SCRIPT_COMPLEX：更复杂的手写风格字体
                todo self.font_cv:  指定TrueType字体文件路径，本方法使用华文行楷

        """

        txt_0 = txt_str + ": {:.2f}".format(input_str)
        font_scale = min(self.image.shape[1] / 640.0, self.image.shape[0] / 480.0) * 0.5  # 条件因子
        text_size = cv2.getTextSize(txt_0, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 2)[0][0]  # 文字长宽
        cv2.putText(self.image, txt_0, (10, (text_size // 10) * pose), font, font_scale, colour,
                    thickness=font_thickness)

    def on_signal_list(self):
        """
        使用定时器发射信号
        """
        if self.humans and self.humans != []:
            self.loggerSignal.emit(self.humans)

    def start_run(self) -> None:
        """
        启动线程
        """
        self.start()
        pass

    def stop(self) -> None:
        """
        终止线程
        """
        self.is_paused = False  # 先暂停线程
        self.wait()  # 等待线程退出
        self.finished.emit()  # 发出完成信号

    def pause(self):
        """
        暂停线程的执行
        """
        self.is_paused = False

    def resume(self):
        """
        恢复线程的执行
        """
        self.is_paused = True

    def kill(self):
        """
        杀死线程
        :return:
        """
        self.stop()
        self.deleteLater()  # 杀死线程

    def on_models(self):
        self.is_open_models = True

    def off_models(self):
        self.is_open_models = False

    def openpose_model(self):
        self.is_DualSwitch = 'openpose'

    def posenet_model(self):
        self.is_DualSwitch = 'posenet'


class Video_MainWindow(QMainWindow):
    def __init__(self, path):
        super().__init__()
        self.worker = Worker_video(WorkerName=None, FilePath=path)  # 创建 Worker_video 实例
        self.setWindowTitle('openpose实时检测')
        self.btn_video = QPushButton('打开摄像头')  # 控制摄像头的状态
        self.lbl_img = QLabel('显示摄像头图像')  # 创建标签控件来显示摄像头的图像， 标签的大小由QGridLayout的布局来决定
        self.lbl_img.setStyleSheet('border: 1px solid black;')  # 给标签设置黑色边框
        self.lbl_img.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 让标签要显示的内容居中
        self.set_label_windows()  # 设置标签大小
        self.btn_video.clicked.connect(self.btn_videos)
        top_widget = QWidget()
        grid = QGridLayout()
        grid.addWidget(self.lbl_img, 0, 0, Qt.AlignmentFlag.AlignTop)  # 放置顶部
        grid.addWidget(self.btn_video, 1, 0, Qt.AlignmentFlag.AlignBottom)  # 放置底部
        top_widget.setLayout(grid)
        self.setCentralWidget(top_widget)
        self.center_win()  # 居中显示主窗口
        self.worker.image_processed.connect(self.update_image)

    def set_label_windows(self):
        self.window_w, self.window_h = self.get_desktop_size()
        self.lbl_img.setMinimumSize(self.window_w * 0.6, self.window_h * 0.6)

    def get_desktop_size(self):
        # 定义获取桌面分辨率的函数
        def get_screen_resolution():
            user32 = ctypes.windll.user32
            screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
            return screensize

        # 获取桌面大小
        self.width, self.height = get_screen_resolution()
        return self.width, self.height

    def center_win(self):
        qr = self.frameGeometry()
        cp = QGuiApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def btn_videos(self):
        if self.worker.is_paused:
            # 启动或恢复图像处理
            self.worker.pause()  # 加锁
            self.btn_video.setText('恢复摄像头')

        else:
            # 暂停图像处理
            self.worker.resume()  # 获取锁
            self.worker.start()  # 启动线程
            self.btn_video.setText('暂停摄像头')

    def update_image(self, pixmap):
        if pixmap is not None:
            self.lbl_img.setPixmap(pixmap.scaled(self.lbl_img.size(), Qt.KeepAspectRatio))
        else:
            print("No image data to display.")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Video_MainWindow('http://47.100.111.106/download_video/鸡你太美.mp4')
    window.show()
    sys.exit(app.exec())
