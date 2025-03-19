import configparser
import requests
from PyQt5.QtCore import QStringListModel, Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QListView, QMessageBox, QPushButton, QLabel, \
    QHBoxLayout, QLineEdit, QDialog, QMenu, QAction, QInputDialog
import sys
from run_app.worker.worker_camre import Worker_carme

config = configparser.ConfigParser()  # 创建configparser对象
config_file_path = '../config.ini'  # 配置文件名为config.ini
config.read(config_file_path)  # 读取配置文件


def read_value_config(keywords, key):
    """
    通过键读取配置文件的值
    :param keywords:默认部分
    :param key:键
    :return:值
    """
    value = config[keywords][key]  # 获取value的值
    return value


def read_config(keywords='CAM'):
    """
    查看config文件的内容
    """
    if keywords not in config.sections():
        config.add_section(keywords)
        with open('../config.ini', 'w') as configfile:  # 将更改写回配置文件
            config.write(configfile)
    default_keys = [key for key in config[keywords] if key not in config['DEFAULT']]  # 获取WEBCAM部分的所有键
    return default_keys


def add_config(keywords='WEBCAM', new_key='new_setting', new_value='some_value'):
    """
    config中添加记录
    :param keywords: 字段
    :param new_key: 添加的键
    :param new_value: 添加的值
    """
    if keywords not in config.sections():  # 检查[WEBCAM]部分是否存在，如果不存在则创建
        config.add_section(keywords)
    config.set(keywords, new_key, new_value)  # 向[WEBCAM]部分添加一个新的键值对
    with open('../config.ini', 'w') as configfile:  # 将更改写回配置文件
        config.write(configfile)
    print(f"Added {new_key}={new_value} to {keywords} section.")


def remove_config(keywords='CAM', key_to_remove='webcam1'):
    """
    config中删除记录
    :param keywords: 字段
    :param key_to_remove: 删除的键
    """
    if keywords in config.sections():  # 检查[CAM]部分是否存在
        if key_to_remove in config[keywords]:  # 检查要删除的键是否存在
            config.remove_option(keywords, key_to_remove)  # 删除[WEBCAM]部分中的指定键
            with open('../config.ini', 'w') as configfile:  # 将更改写回配置文件
                config.write(configfile)
            print(f"Removed {key_to_remove} from [{keywords}] section.")
            return 1
        else:
            print(f"Key {key_to_remove} does not exist in [{keywords}] section.")
            return 0
    else:
        print("Section [{keywords}] does not exist.")
        config.add_section(keywords)
        # return None


def load_icon(path):
    """加载图标"""
    pixmap = QPixmap(path)
    return QIcon(pixmap)


def rename_config(keywords='WEBCAM', old_key='old_key', new_key='new_key'):
    """
    重命名key
    :param keywords: 字段
    :param old_key: 旧键
    :param new_key: 新键
    :return:
    """
    try:
        # 检查[WEBCAM]部分是否存在
        if keywords in config:
            # 检查webcam2键是否存在
            if old_key in config[keywords]:
                value = config.get(keywords, old_key)  # 读取webcam2的值
                config.remove_option(keywords, old_key)  # 删除旧的键webcam2
                config.set(keywords, new_key, value)  # 添加新的键webcam3，并赋予相同的值
                with open(config_file_path, 'w') as configfile:  # 将修改后的配置写回文件
                    config.write(configfile)
                return {new_key, value}
            else:
                return None
        else:
            return 0
    except configparser.NoSectionError as e:
        print(f"Error: {e}")
    except configparser.NoOptionError as e:
        print(f"Error: {e}")


def update_listview(listview, keywords: str = 'CAM'):
    """
    构建文件模型
    """
    qlist = read_config(keywords)
    slm = QStringListModel()
    slm.setStringList(qlist)  # 列表
    listview.setModel(slm)
    return qlist


class CamInputDialog(QDialog):
    """
    添加本地摄像头输入框
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle('添加摄像头')
        self.setMinimumSize(300, 200)

        # 创建布局
        layout_v1 = QVBoxLayout()
        layout_h1 = QHBoxLayout()
        layout_h2 = QHBoxLayout()
        layout_h3 = QHBoxLayout()

        # 创建组件
        self.label1 = QLabel('别名')
        self.input1 = QLineEdit()
        self.label2 = QLabel('索引')
        self.input2 = QLineEdit()
        self.label3 = QLabel('提示！摄像头索引为int类型的数字')
        self.confirm_button = QPushButton('保存')
        self.cancel_button = QPushButton('取消')

        layout_h1.addWidget(self.label1)
        layout_h1.addWidget(self.input1, 1)
        layout_h1.addWidget(self.label2)
        layout_h1.addWidget(self.input2, 1)
        layout_h2.addWidget(self.confirm_button)
        layout_h2.addWidget(self.cancel_button)
        layout_v1.addLayout(layout_h1)
        layout_v1.addWidget(self.label3)
        layout_v1.addLayout(layout_h2)
        self.setLayout(layout_v1)

        # 连接按钮的点击事件
        self.confirm_button.clicked.connect(self.on_confirm)
        self.cancel_button.clicked.connect(self.on_cancel)

    def on_confirm(self):
        """
        保存按钮的槽函数
        :return:
        """
        input_text1 = self.input1.text()
        input_text2 = self.input2.text()
        if input_text1 == '' or input_text2 == '':
            QMessageBox.warning(self, '错误！', '别名、摄像头索引不能为空')
        else:
            add_config(keywords='CAM', new_key=input_text1, new_value=input_text2)
            QMessageBox.information(self, '添加摄像头？', f'您已经成功添加{input_text1}摄像')
            self.accept()  # 关闭对话框

    def on_cancel(self):
        """
        关闭对话框
        """
        self.reject()


class Cam_ListView(QWidget):
    """
    摄像头设备列表视图
    """
    Cam_Signal = pyqtSignal(str)  # 用于点击后发送摄像头的信息
    """
    摄像头列表
    """

    def __init__(self):
        super().__init__()
        self.key = None
        self.qModelIndex = None
        self.Worker_carme = None
        self.is_open_moldes = None
        self.qlist = None
        self.setWindowTitle("摄像头列表")
        self.resize(300, 200)
        layout = QVBoxLayout()

        # 创建组件并构建本地摄像头模型listview1
        label1 = QLabel('摄像头列表')
        self.listview1 = QListView()
        self.qlist1 = update_listview(self.listview1)  # 构建或更新模型
        self.add_cam_button = QPushButton("添加摄像头", self)  # 创建添加摄像头的按钮

        # 布局设计
        layout.addWidget(label1)
        label1.setAlignment(Qt.AlignCenter)  # 设置 QLabel 的对齐方式
        layout.addWidget(self.listview1)
        layout.addWidget(self.add_cam_button)
        self.setLayout(layout)

        self.cam_dialog = CamInputDialog()  # 创建对话框实例

        # 创建上下文菜单
        self.context_menu = QMenu()
        self.action_delete = QAction('删除', self)
        self.action_edit = QAction('修改', self)
        # 将动作添加到上下文菜单
        self.context_menu.addAction(self.action_delete)
        self.context_menu.addAction(self.action_edit)

        # 信号连接
        self.listview1.clicked.connect(self.clicked1)
        self.add_cam_button.clicked.connect(self.on_add_cam_button)
        self.listview1.setContextMenuPolicy(Qt.CustomContextMenu)  # 设置自定义上下文菜单
        self.action_delete.triggered.connect(self.on_delete)
        self.action_edit.triggered.connect(self.on_edit)
        self.listview1.customContextMenuRequested.connect(self.show_context_menu)

    def on_delete(self):
        """
        点击删除的槽函数
        """
        index = self.listview1.selectedIndexes()[0]  # 假设只有一个选中项
        if index.isValid():
            self.key = self.qlist1[index.row()]
            if QMessageBox.question(self, '删除', f'你确定要删除摄像头{self.key}?',
                                    QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                remove_config(key_to_remove=self.key)
                self.qlist1 = update_listview(self.listview1)
        else:
            pass

    def on_edit(self):
        """
        点击修改的槽函数
        """
        index = self.listview1.selectedIndexes()[0]  # 假设只有一个选中项
        if index.isValid():
            self.key = self.qlist1[index.row()]
            new_text, select = QInputDialog.getText(self, '摄像头重名', '请输入新名称')
            if select and new_text != '':
                if QMessageBox.question(self, '修改', f'你确定要修改摄像头{self.key}的名称{new_text}吗?',
                                        QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                    rename_config(keywords='CAM', old_key=self.key, new_key=new_text)
                    self.qlist1 = update_listview(self.listview1)

    def show_context_menu(self, pos):
        """
        右击事件的槽函数（上下文对话框）
        :param pos: 弹窗框的位置
        """
        self.context_menu.exec_(self.listview1.viewport().mapToGlobal(pos))

    def on_add_cam_button(self):
        """
        添加摄像的槽函数
        """
        self.cam_dialog.exec_()  # 显示对话框并等待用户操作
        self.qlist1 = update_listview(self.listview1)

    def clicked1(self, qModelIndex):
        """
        self.qlist2[qModelIndex.row()]获取模型中某一列的值
        :param qModelIndex:显示和处理数据的通用框架，这些数据可以是树状结构的，
        :return:值
                列表视图（QListView）、表格视图（QTableView）等。
        QModelIndex 包含以下关键信息：
        行（Row）：项在模型中的行号。
        列（Column）：项在模型中的列号。
        父模型指针（Parent Model Pointer）：指向项所属的模型对象的指针。
        以下是一些关于 QModelIndex 的常见用法：
        选择和高亮显示：您可以使用 QModelIndex 来选择和高亮显示视图中的特定项。
        导航：QModelIndex 支持行和列的导航，您可以获取一个项的父项、子项、兄弟项或移动到下一个/上一个项。
        比较：可以比较两个 QModelIndex 对象以检查它们是否相等或一个是否在另一个之前。
        无效状态：QModelIndex 可以是无效的，这通常表示它不引用模型中的任何项。
        """
        self.qModelIndex = qModelIndex
        value = read_value_config('CAM', self.qlist1[self.qModelIndex.row()])

        self.start_worker(value)
        self.Cam_Signal.emit(value)
        return value

    def start_worker(self, value):
        """
        启动摄像头
        :param value:
        """
        try:
            self.Worker_carme.stop()
        except AttributeError:
            pass
        except RuntimeError:
            pass
        try:
            value = int(value)
            self.Worker_carme = Worker_carme(Camera_Index=value)
            self.Worker_carme.start()
            QMessageBox.information(self, "成功启动摄像头", self.qlist1[self.qModelIndex.row()] + "本地摄像头加载成功")
        except AttributeError as e:
            print(f"发生 AttributeError: {e}")
            QMessageBox.warning(self, "启动摄像头失败",
                                f"系统检测到该摄像头索引没有摄像头资源，请检查本地摄像头索引{value}是否正确？（建议设置0或1），报错信息{e}")
        except ValueError as e:
            try:
                if self.get_camera_stream(value):
                    self.Worker_carme = Worker_carme(Camera_Index=value)
                    self.Worker_carme.start()
                    QMessageBox.information(self, "成功启动摄像头",
                                            self.qlist1[self.qModelIndex.row()] + "网络摄像头加载成功")
                else:
                    print(f"发生异常")
            except AttributeError as e:
                print(f"发生 AttributeError: {e}")
                QMessageBox.warning(self, "启动摄像头失败",
                                    f",系统检测到该URL没有摄像头资源，请检查ip摄像头url:{value}是否正确？报错信息{e}")

    def get_camera_stream(self, url, timeout=2):
        """

        :param url:
        :param timeout:
        :return:
        """
        try:
            # 发送请求并设置超时时间
            response = requests.get(url, timeout=timeout, stream=True)  # 设置stream=True来处理流数据
            # 输出HTTP状态码
            print(f"HTTP Status Code: {response.status_code},{url}有可用的摄像头资源")
            if response.status_code == 200:  # 检查响应状态码，如果不是200，则可能是错误
                return 1
            elif response.status_code != 200:
                response.raise_for_status()
                return 0
        except requests.exceptions.HTTPError as e:  # 会捕获到4xx和5xx的错误响应
            print(f"HTTP Error occurred: {e}")
            QMessageBox.warning(self, "HTTP 错误", f"报错信息{e}")
        except requests.exceptions.Timeout as e:  # 会捕获到请求超时的情况
            print("The request timed out.")
            QMessageBox.warning(self, "连接摄像头超时",
                                f"请保证网络畅通，ip摄像头{self.qlist1[self.qModelIndex.row()]}可正常访问？报错信息{e}")
        except requests.exceptions.RequestException as e:  # 会捕获到请求异常的情况
            print(f"A requests error occurred: {e}")
            QMessageBox.warning(self, "请求异常",
                                f"请求错误，ip摄像头{self.qlist1[self.qModelIndex.row()]}URL错误！报错信息{e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Cam_ListView()
    win.show()
    sys.exit(app.exec_())
