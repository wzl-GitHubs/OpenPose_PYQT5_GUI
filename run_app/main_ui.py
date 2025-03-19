# -*- coding: utf-8 -*-

import configparser
import logging
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QMainWindow
from run_app.Window.window_camre import Cam_MainWindow as Cams
from run_app.Window.window_video import Video_MainWindow as Videos
from run_app.Window.window_image import MainWindow as Worker_Image
from run_app.MarkdownViewer import MarkdownViewer as Markdown_window

config = configparser.ConfigParser()  # 创建配置解析器


def read_config(key: str, config_path: str = '../config.ini', key_word: str = 'DEFAULT'):
    """
    读取配置文件
    :param key: 键
    :param config_path: 配置文件的路径
    :param key_word: 配置问价的关键字段
    :return: 配置文件关键字段下键所对应的值
    """
    config.read(config_path)  # 读取配置文件
    key_value = config[key_word][key]
    return key_value


def read_list(list_str: str):
    """
    读取配置文件的记录的列表，这里是显示的文件的格式
    :param list_str:
    :return:列表
    """
    list_value = [item.strip("'") for item in list_str.split(', ')]
    return list_value


service_url_video = read_config(key='service_url_video')
service_url_image = read_config(key='service_url_image')
video_type_list_str = read_config(key='video_type_list')
image_type_list_str = read_config(key='image_type_list')
markdown_file_path = read_config(key='markdown_file_path')
video_type_list = read_list(list_str=video_type_list_str)
image_type_list = read_list(list_str=image_type_list_str)


class Func():
    def __init__(self):
        self.ThemeSwitch = False

    def cam_func(self):
        """实例化摄像头模块 :return: 摄像头模块对像"""
        cam = Cams(ThemeSwitch=self.ThemeSwitch)
        return cam

    def video_func(self):
        """实例化视频模块 :return: 视频模块对象"""
        video = Videos(type_list=video_type_list, service_url=service_url_video, ThemeSwitch=self.ThemeSwitch)
        return video

    def image_func(self):
        """实例化图片模块 :return: 图片模块对象"""
        Image = Worker_Image(image_type_list, service_url_image, ThemeSwitch=self.ThemeSwitch)
        return Image


def markdown_func():
    """实例化markdown模块 :return: markdown模块对象"""
    markdown_viewer = Markdown_window(markdown_file_path)  # 创建 MarkdownViewer 实例
    return markdown_viewer


class Ui_MainWindow(QMainWindow):
    """
    主窗口
    """

    def __init__(self):
        super().__init__()
        self.func = Func()
        self.create_window_Object = None
        self.image_label = None
        self.logger = logging.getLogger(__name__)
        self.main_window = QPixmap('../resources/icon/main_windows_mast.png')
        self.icon_window = QIcon('../resources/icon/posewindow.png')
        self.setWindowIcon(self.icon_window)

    def setupUi(self, MainWindow):
        """
        创建主窗口
        :param MainWindow:
        """
        MainWindow.setObjectName("MainWindow")
        # MainWindow.resize(1124, 840)
        MainWindow.resize(1224, 840)
        font = QtGui.QFont()
        font.setFamily("华文琥珀")
        font.setPointSize(10)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        MainWindow.setFont(font)
        MainWindow.setWindowIcon(self.icon_window)
        MainWindow.setStyleSheet("font: 10pt \"华文琥珀\";\n"
                                 "QPushButton\n"
                                 "                     {text-align : center;\n"
                                 "                     background-color : white;\n"
                                 "                     font: bold;\n"
                                 "                     border-color: ;\n"
                                 "    color: rgb(255, 255, 255);\n"
                                 "                     border-width: 5px;\n"
                                 "                     border-radius: 10px;\n"
                                 "                     padding: 6px;\n"
                                 "                     height : 14px;\n"
                                 "                     border-style: outset;\n"
                                 "                     font : 14px;}\n"
                                 "                     QPushButton:pressed\n"
                                 "                     {text-align : center;\n"
                                 "                     background-color : light gray;\n"
                                 "                     font: bold;\n"
                                 "                     border-color: gray;\n"
                                 "                     border-width: 2px;\n"
                                 "                     border-radius: 10px;\n"
                                 "                     padding: 6px;\n"
                                 "                     height : 14px;\n"
                                 "                     border-style: outset;\n"
                                 "                     font : 14px;\n"
                                 "                     sub-control-position: center}\n"
                                 "")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setStyleSheet("")
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setContentsMargins(5, 5, 5, 5)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")

        self.verticalLayout.addWidget(self.tabWidget)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1280, 120))
        self.menubar.setObjectName("menubar")

        self.menu_main = QtWidgets.QMenu(self.menubar)
        self.menu_main.setObjectName("menu_main")
        self.cameraDetection = QtWidgets.QAction(MainWindow)
        self.cameraDetection.setObjectName("cameraDetection")
        self.videoDetection = QtWidgets.QAction(MainWindow)
        self.videoDetection.setObjectName("videoDetection")
        self.imageDetection = QtWidgets.QAction(MainWindow)
        self.imageDetection.setObjectName("imageDetection")

        self.menu_main.addAction(self.cameraDetection)
        self.menu_main.addSeparator()
        self.menu_main.addAction(self.videoDetection)
        self.menu_main.addSeparator()
        self.menu_main.addAction(self.imageDetection)

        self.menu_set = QtWidgets.QMenu(self.menubar)
        self.menu_set.setObjectName("menu_set")
        self.setTheme = QtWidgets.QAction(MainWindow)
        self.setTheme.setObjectName("setTheme")

        self.menu_main.addSeparator()
        self.menu_set.addAction(self.setTheme)
        self.menu_main.addSeparator()

        self.menu_about = QtWidgets.QMenu(self.menubar)
        self.menu_about.setObjectName("menu_about")
        MainWindow.setMenuBar(self.menubar)

        # 创建帮助上下文菜单栏
        self.about_us = QtWidgets.QAction(MainWindow)
        self.about_us.setObjectName("about_us")
        self.assist = QtWidgets.QAction(MainWindow)
        self.assist.setObjectName("assist")
        self.feedback = QtWidgets.QAction(MainWindow)
        self.feedback.setObjectName("feedback")

        # 添加模块按钮
        self.menu_about.addAction(self.about_us)
        self.menu_main.addSeparator()
        self.menu_about.addAction(self.assist)
        self.menu_main.addSeparator()
        self.menu_about.addAction(self.feedback)

        self.menubar.addAction(self.menu_main.menuAction())
        self.menubar.addAction(self.menu_set.menuAction())
        self.menubar.addAction(self.menu_about.menuAction())

        self.image_label = QLabel(MainWindow)
        self.image_label.setObjectName("image_label")
        self.image_label.setPixmap(QPixmap(self.main_window))
        self.image_label.setScaledContents(True)  # 设置图像可缩放以填充整个标签
        self.image_label.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        MainWindow.setCentralWidget(self.image_label)

        self.welcome_label = QtWidgets.QLabel("欢迎使用openpose", self.centralwidget)
        self.welcome_label.setObjectName("welcome_label")
        self.verticalLayout.addWidget(self.welcome_label)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # 连接信号槽
        self.cameraDetection.triggered.connect(self.CameraDetectionWindow)
        self.videoDetection.triggered.connect(self.videoDetectionWindow)
        self.imageDetection.triggered.connect(self.imageDetectionWindow)
        self.assist.triggered.connect(self.MarkdownDetectionWindow)
        self.setTheme.triggered.connect(self.on_setTheme)
        # print(MainWindow.width())
        # print(type(MainWindow.width()))
        """
        窗口位置信息和窗口长宽
        """
        self.window_0 = MainWindow
        self.mainwidth = MainWindow.width()
        self.mainheight = MainWindow.height()
        self.posex = MainWindow.pos().x()
        self.posey = MainWindow.pos().y()
        # print(type(self.posex))
        # print(self.posex)
        """"
        因为窗口的位置信息和大小信息qt中返回的是某一时刻的值，需要重写on_resize和on_move方法
        """

        #
        def on_resize(event):
            self.mainwidth = event.size().width()
            self.mainheight = event.size().height()

        # 重写 moveEvent 方法
        def on_move(event):
            self.posex = event.pos().x()
            self.posey = event.pos().y()

        # 将重写的方法设置到 QMainWindow 实例上
        MainWindow.resizeEvent = on_resize
        MainWindow.moveEvent = on_move

    def on_resize(self, event):
        # 更新窗口宽度和高度
        self.mainwidth = self.window_0.width()
        self.mainheight = self.window_0.height()

    def on_move(self, event):
        # 更新窗口位置
        self.posex = self.window_0.pos().x()
        self.posey = self.window_0.pos().y()

    def on_setTheme(self):
        _translate = QtCore.QCoreApplication.translate
        if not self.func.ThemeSwitch:
            self.func.ThemeSwitch = True
            self.setTheme.setText(_translate("MainWindow", "关闭暗黑模式"))
        elif self.func.ThemeSwitch:
            self.func.ThemeSwitch = False
            self.setTheme.setText(_translate("MainWindow", "打开暗黑模式"))

    def create_window(self, func_name, ObjectName, WindowTitle, close_event):
        """
        创建弹出的窗口
        :param func_name: 实现窗口的函数
        :param ObjectName: 定义的对象名
        :param WindowTitle: 窗口标签
        :param close_event: 重写关闭事件
        """
        self.window_0.hide()
        self.create_window_Object = func_name()
        self.create_window_Object.setObjectName(ObjectName)
        self.create_window_Object.setWindowTitle(WindowTitle)
        self.create_window_Object.setGeometry(self.posex, self.posey, self.mainwidth, self.mainheight)
        self.create_window_Object.show()
        self.create_window_Object.closeEvent = close_event
        return self.create_window_Object

    def MarkdownDetectionWindow(self):
        """帮助文档窗口的创建"""
        self.markdown_window = self.create_window(markdown_func, 'assist_window', '帮助说明文档',
                                                  self.markdown_close_event)

    def CameraDetectionWindow(self):
        """创建摄像头检测窗口"""
        self.cam_window = self.create_window(self.func.cam_func, "human_pose_detection_window", "摄像头检测",
                                             self.cam_close_event)

    def videoDetectionWindow(self):
        """创建视频检测窗口"""
        self.video_window = self.create_window(self.func.video_func, "human_pose_recognition_window", "视频检测",
                                               self.video_close_event)

    def imageDetectionWindow(self):
        """创建图片检测窗口"""
        self.image_window = self.create_window(self.func.image_func, "Image_detection_window", "图片检测",
                                               self.image_close_event)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "openpose人体姿态检测"))

        self.menu_main.setTitle(_translate("MainWindow", "主要功能"))
        self.cameraDetection.setText(_translate("MainWindow", "摄像头检测"))
        self.videoDetection.setText(_translate("MainWindow", "视频流检测"))
        self.imageDetection.setText(_translate("MainWindow", "图片检测"))

        self.menu_set.setTitle(_translate("MainWindow", "设置"))
        self.setTheme.setText(_translate("MainWindow", "切换主题"))

        self.menu_about.setTitle(_translate("MainWindow", "帮助"))
        self.about_us.setText(_translate("MainWindow", "关于我们"))
        self.assist.setText(_translate("MainWindow", "说明帮助"))
        self.feedback.setText(_translate("MainWindow", "反馈"))

    def cam_close_event(self, event):
        """
        关闭摄像头窗口
        :param event:
        """
        try:
            if self.cam_window:
                self.cam_window.list_cam_widget.Worker_carme.pause()  # 加锁
                self.cam_window.list_cam_widget.Worker_carme.stop()
                self.cam_window.list_cam_widget.Worker_carme.deleteLater()
            self.window_0.show()
        except:
            self.window_0.show()

    def video_close_event(self, event):
        """
        关闭视频检测窗口
        :param event:
        """
        try:
            if self.video_window and hasattr(self.video_window.file_widget, 'Worker_video'):
                self.video_window.file_widget.Worker_video.stop()  # 安全停止线程
            self.video_window.deleteLater()  # 安排窗口稍后删除
        except Exception as e:
            # 记录具体的异常信息
            logging.error(f"Error handling close event: {e}")
        finally:
            self.window_0.show()  # 无论如何都显示新窗口

    def image_close_event(self, event):
        """
        关闭图片处理窗口
        :param event:
        """

        if self.image_window:
            self.window_0.show()


    def markdown_close_event(self, event):
        if self.markdown_window:
            self.window_0.show()



if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(window)
    window.show()
    app.exec_()  # 启动事件循环
