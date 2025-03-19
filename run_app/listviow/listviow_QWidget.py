import logging
import sys

import requests
from PyQt5.QtCore import QDir, Qt, QAbstractListModel, QModelIndex, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QListView, QFileIconProvider, QFileSystemModel, QVBoxLayout, \
    QWidget, QPushButton, QFileDialog, QMessageBox, QFrame, QLabel
from bs4 import BeautifulSoup

from run_app.worker.worker_image import FileProcessingThread
from run_app.worker.worker_video import Worker_video


class PyAndTxtFileFilterModel(QFileSystemModel):
    def __init__(self, parent=None, type_list=None):
        super(PyAndTxtFileFilterModel, self).__init__(parent)
        self.setRootPath("../../resources/videos/")
        self.setFilter(QDir.Files | QDir.Dirs | QDir.NoDotAndDotDot | QDir.NoSymLinks)
        self.setNameFilters(type_list)



class RemoteFileModel(QAbstractListModel):
    """
    读取service文件的类
    """
    def __init__(self, parent=None, service_url="http://47.100.111.106/download_video/"):
        super(RemoteFileModel, self).__init__(parent)
        self.service_url = service_url
        self.fileList = []

    def rowCount(self, parent=QModelIndex()):
        return len(self.fileList)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or index.row() >= len(self.fileList):
            return None
        if role == Qt.DisplayRole:
            file_info = self.fileList[index.row()]
            return file_info  # file_info 是一个字符串，直接返回它

    def fetchFiles(self):
        try:
            response = requests.get(self.service_url, timeout=5)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                files = soup.find_all('a')
                self.fileList = [file.text for file in files]
                self.beginResetModel()  # 开始重置模型
                self.endResetModel()  # 结束重置模型
        except requests.RequestException:
            QMessageBox.warning(self.parent(), "警告", "无法获取文件列表，请检查网络是否连接或网页链接的是否有效。")


class FileBrowser(QWidget):
    """
    type_list；过滤列表
    file_path；本地文件打开的默认目录
    service_url；服务器地址的url
    WorkerName；模块调用标签
    """
    filepath_Signal = pyqtSignal(str)

    def __init__(self, parent=None, type_list=None, file_path="../resources/videos",
                 service_url='http://47.100.111.106/download_video', WorkerName='video'):
        super(FileBrowser, self).__init__(parent)
        self.Worker_image = None
        self.Worker_video = None
        self.WorkerName = WorkerName
        self.fileModel = None  # 初始化本地文件模型
        self.model_url = None  # 初始化网络文件模型
        self.is_openurl = 1  # 连接服务器的标记

        # 创建组件
        self.listview1 = QListView()
        self.openFolderButton = QPushButton("切换目录", self)  # 创建打开文件夹按钮
        self.vertical_separator = QFrame()  # 水平分割
        self.label1 = QLabel('本地文件')
        self.label2 = QLabel('服务器文件')
        self.listView2 = QListView(self)
        self.linkButton = QPushButton("链接", self)

        # 创建两个文件浏览器
        self.local_file_model(type_list, file_path=file_path)
        self.network_file_model(service_url)

        # 创建 QVBoxLayout 并将 QListView1->2 和按钮添加到布局中
        layout = QVBoxLayout(self)
        layout.addWidget(self.label1)
        self.label1.setAlignment(Qt.AlignCenter)  # 设置标签文本居中
        layout.addWidget(self.listview1, 2)
        layout.addWidget(self.openFolderButton)
        layout.addWidget(self.vertical_separator)
        layout.addWidget(self.label2)
        self.label2.setAlignment(Qt.AlignCenter)  # 设置标签文本居中
        layout.addWidget(self.listView2, 2)
        layout.addWidget(self.linkButton)

        # 连接信号槽
        self.listview1.doubleClicked.connect(self.openDirectory)
        self.openFolderButton.clicked.connect(self.onOpenFolderButtonClicked)
        self.listView2.doubleClicked.connect(self.onFileClicked)  # 点击服务器文件系统的信号连接
        self.linkButton.clicked.connect(self.LinkClicked)

    def local_file_model(self, type_list, file_path="/"):
        """
        创建本地文件模型
        :param file_path: 文件浏览器默认打开的地址
        :param type_list: 不过滤文件的后缀列表
        """
        self.fileModel = PyAndTxtFileFilterModel(type_list=type_list)
        self.fileModel.setRootPath("/")
        # self.fileModel.setIconProvider(QFileIconProvider())
        self.listview1.setModel(self.fileModel)  # 创建本地文件浏览器
        print(str(self.fileModel.index(file_path)))

        self.listview1.setRootIndex(self.fileModel.index(file_path))

    def network_file_model(self, service_url):
        """
        服务器文件系统模型
        :param service_url:网络URL地址
        """
        self.model_url = RemoteFileModel(self, service_url=service_url)
        self.listView2.setModel(self.model_url)  # 创建网络文件浏览器实例

    def onOpenFolderButtonClicked(self):
        """
        使用 QFileDialog 获取用户选择的本地文件夹路径
        """
        directoryPath = QFileDialog.getExistingDirectory(self, "选择文件夹", "")
        if directoryPath:
            self.fileModel.setRootPath(directoryPath)  # 更新文件模型的根路径
            self.listview1.clearSelection()  # 清除 QListView 的选择
            self.listview1.setRootIndex(
                self.fileModel.index(directoryPath))  # 更新 QListView 的根索引
            self.fileModel.setRootPath(directoryPath)
            print(directoryPath)

    def openDirectory(self, index):
        """
        获取本地文件地址，并启动模型
        :param index:
        """
        filePath = self.fileModel.filePath(index)
        if self.WorkerName == "video":
            self.start_werker_video(filePath)
        elif self.WorkerName == 'image':
            self.start_werker_image(filePath)
        else:
            logging.info('模块参数错误')
        print("Selected:", filePath)

    def LinkClicked(self):
        """
        连接服务器数据的按钮
        """
        if self.is_openurl == 1:
            self.model_url.fetchFiles()
            self.model_url.layoutAboutToBeChanged.emit()  # 通知视图布局即将改变
            self.model_url.layoutChanged.emit()  # 通知视图布局已改变
            self.linkButton.setText("断开")
            self.is_openurl = 0
        elif self.is_openurl == 0:
            # 清空文件列表并重置模型
            self.model_url.fileList = []
            self.model_url.beginResetModel()  # 开始重置模型
            self.model_url.endResetModel()  # 结束重置模型
            self.linkButton.setText("链接")
            self.is_openurl = 1

    def onFileClicked(self, index):
        """
        获取服务器文件地址，并启动模型
        :param index:
        """
        file_name = self.model_url.data(index, Qt.DisplayRole)  # 获取被点击的文件名
        full_url = self.model_url.service_url + file_name  # 构建完整的 URL 地址
        if full_url.endswith('/'):
            QMessageBox.information(self, "错误", "请选择打开视频或图片文件打开")
        else:
            print("Selected file URL:", full_url)  # 打印完整的 URL 地址
            if self.WorkerName == "video":
                self.start_werker_video(full_url)
            elif self.WorkerName == 'image':
                self.start_werker_image(full_url)
            else:
                logging.info('模块参数错误')

    def start_werker_video(self, path):
        try:
            self.Worker_video.kill()  # 安全杀死线程
        except:
            print('请选择合适的文件打开')
        try:
            self.Worker_video = Worker_video(FilePath=path)
            self.Worker_video.pause()
            self.Worker_video.start()  # 启动线程
            self.filepath_Signal.emit(path)
            QMessageBox.information(self, "提醒", "数据加载成功！\n地址：" + path)
        except:
            QMessageBox.information(self, "错误", "请选择文件打开")

    def start_werker_image(self, path):
        try:
            self.Worker_image.kill()  # 安全杀死线程
        except:
            print('请选择合适的文件打开')
        try:
            self.Worker_image = FileProcessingThread(image_path=path)
            self.Worker_image.resume()
            self.Worker_image.start()  # 启动线程
            self.filepath_Signal.emit(path)
        except:
            QMessageBox.information(self, "错误", "请选择文件打开")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = QMainWindow()
    WorkerName = 'video'
    # WorkerName = 'image'
    if WorkerName == 'video':
        service_url = 'http://47.100.111.106/download_video/22'
        type_list = ['*.mp4', '*.avi', '*.mkv', '*.mov', '*.wmv', '*.flv', '*.f4v', '*.webm', '*.m4v',
                     '*.ts', '*.mpeg', '*.mpe', '*.mpg', '*.rm', '*.rmvb', '*.vob', '*.m2ts', '*.dts']
        file_path = "../../resources/videos/"
        central_widget = FileBrowser(type_list=type_list, service_url=service_url, file_path=file_path,
                                     WorkerName=WorkerName)
        main_window.setCentralWidget(central_widget)  # 设置 central_widget 为 main_window 的中心部件
        main_window.show()  # 显示主窗口
        sys.exit(app.exec_())

    elif WorkerName == 'image':
        type_list = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.gif', '*.tiff']
        service_url = 'http://47.100.111.106/download_image/'
        file_path = "../../resources/images/"
        central_widget = FileBrowser(type_list=type_list, service_url=service_url, file_path=file_path,
                                     WorkerName=WorkerName)

        main_window.setCentralWidget(central_widget)  # 设置 central_widget 为 main_window 的中心部件
        main_window.show()  # 显示主窗口
        sys.exit(app.exec_())
