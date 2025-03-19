# 系统实现

## 5.1 主界面实现

为了方便系统的维护，提高代码的可读性，增加模块化功能的部署，本系统所有UI界面未使用qt设计师，UI风格有两套，分别是默认模式和黑暗模式，主页面主要实现系统三大模块线程的管理、UI的风格的切换、以及本系统说明的文档的渲染。下图分别是系统主界面图5.1、摄像头姿态检测模块图5.2、本地视频姿态检测模块图5.3、图片检测模块图5.4。

<img title="" src="file:///C:/Users/19124/AppData/Roaming/marktext/images/2024-05-28-03-43-54-image.png" alt="" width="667">

图5.1 主窗口UI

![](C:\Users\19124\AppData\Roaming\marktext\images\2024-05-28-03-45-12-image.png)

图5.2摄像头姿态估计页面

![](C:\Users\19124\AppData\Roaming\marktext\images\2024-05-28-03-45-58-image.png)

图5.3视频姿态估计页面

![](C:\Users\19124\AppData\Roaming\marktext\images\2024-05-28-03-47-38-image.png)

图5.4视频姿态估计页面

## 5.2 摄像头列表视图的实现

系统各功能模块的UI界面最左侧是显示文件系统或设备ID的自定义列表视图，对于摄像头的文件模型需要自定义，为了提高系统的灵活性，本系统将课题中涉及到的重要参数全部放在，config配置文件中，读取摄像头信息的时候运用configparser库读取配置文件config.ini中的记录，既提高了系统的灵活性，又实现了摄像头设备记录的永久存储。为了实现本课题的设计需求，对config文件增删改查分装了以下四个方法，具体实现代码如下。

```python
import
configparser
config = configparser.ConfigParser() 
config_file_path = '../config.ini' 
config.read(config_file_path) 

def read_value_config(keywords, key):
    value = config[keywords][key] 
    return value

def read_config(keywords='CAM'):
    if keywords not in config.sections():
        config.add_section(keywords)
        with open('../config.ini', 'w') as configfile:
            config.write(configfile)

    default_keys = [key for key in config[keywords] if key not in config['DEFAULT']] 
    return
        default_keys

def add_config(keywords,new_key='new_setting', new_value='some_value'):

    if keywords not in config.sections():
        config.add_section(keywords)
        config.set(keywords,new_key, new_value)
        with open('../config.ini', 'w') as configfile: 
            config.write(configfile)
        print(f"Added {new_key}={new_value} to {keywords} section.")

def remove_config(keywords='CAM', key_to_remove='webcam1'):
    if keywords in config.sections(): 
        if key_to_remove in config[keywords]:
            config.remove_option(keywords,key_to_remove)
            with open('../config.ini', 'w') as configfile:
                config.write(configfile)
            print(f"Removed {key_to_remove} from [{keywords}] section.")
            return 1
        else:
            print(f"Key {key_to_remove} does not exist in [{keywords}] section.")
            return 0
    else:
        print("Section [{keywords}] does not exist.")
        return None

def rename_config(keywords='WEBCAM',old_key='old_key', new_key='new_key'):
    try:
        if keywords in config:
            if old_key in config[keywords]:
                value = config.get(keywords,old_key) 
                config.remove_option(keywords,old_key) 
                config.set(keywords, new_key,value) 

                with open(config_file_path, 'w') as configfile:
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

```

增加摄像头设备输入对话框的UI设计如图5.5，当输入满足条件时，点击保存按钮，程序会将增加的设备信息写入到config文件中，此处调用了添加配置文件记录的函数add_config，然后调用重构自定义列表视图的槽函数，最后将用户新添加的设备刷新显示到列表视图中。

图5.5 添加摄像头输入对话框

删除和修改摄像头设备弹出框的UI设计如图5.6，当右击已经创建的摄像头设备时会在鼠标右击的位置出现一个弹出框，与此同时程序会将摄像头设备信息的别名作为一个字符串类型的信号发射出去，此处需要自定义右击事件，自定义的右击事件实现的方法名为show_context_menu，若再点击弹出的删除按钮，与删除按钮连接的槽函数会立即调remove_config函数，remove_config函数会将发出的字符串类型的信号作为参数传入，然后删除配置文件config.ini指定的某一条记录，最后重新创建了一下列表视图，以刷新列表视图中已删除的摄像头设备。当点击修改时，在桌面会弹出摄像头重命名的弹出对话框如图5.7所示，若在输入框中输入的字段有效，当点击Ok按钮后，OK按钮的槽函数将调用修改配置文件config.ini记录的函数rename_config，rename_config函数接收两个参数，其中一个为用户在文本框中输入的值，另一个是用户右击时选中的摄像头设备的别名，rename_config函数会将配置文件中摄像头原始的别名替换为用户输入的别名，最后重新构建列表视图，以刷新列表视图中已修改的摄像头设备。

整个系统摄像头设备的列表视图最复杂，首先摄像头设备列表视图是用户自定义的，难免会有用户输错摄像头设备索引或URL的情况，尤其是当用户自定义网络摄像头的时候，很容易输错摄像头的URL地址，即便是网络摄像头的URL是正确的，也有可能出现摄像头离线或计算机未接入互联网的情况，在这些复杂的情况下，当用户点击了错误或无法连接的摄像头的时候，很容易造成系统崩溃。

|     |
| --- | --- |
|     |     |

 

图5.6  自定义右键弹出框                 图5.7 修改摄像头输入框

其次就是opencv本身不具备判断网络摄像头是否可连接的处理机制，再加上本地摄像头传入的参数是int类型的整数，网络摄像头的URL为str类型的字符串，所系统还需要对文本框中的字符做一个判断，然后再通过不同的方法连接摄像头。要想在一个模块中实现所有的功能，无疑是很大的挑战。以下是本课题的解决方案。

本系统具有强大的报错处理机制，可以迅速的判断摄像头设备是否可以连接。其实现原理是利用分阶段异常处理的思想，对第一阶段的抛出异常再做了一次异常的捕获，最后对第二阶段产生的异常进行分析，并将分析出的错误类型以弹出框的形式显示在桌面系统上。

第一阶段，当传入的参数是int类型时，判断该int类型参数是否为可用的摄像头设备的索引，如果可用，则弹出设备加载成功的提醒对话框5.8所示，否则将弹出报错对话框如图5.9所示。

图5.8摄像头加载成功弹出框                图5.9本地摄像头加载错误弹出框

第二阶段，当传入参数是str类型时，程序抛出异常，对该异常的处理方法是又做第一次异常的捕获。若第二次捕获到了异常，则弹出所出错类型的具体信息，如图5.10所示。第二次异常的类型一般有请求错误、连接超时、请求异常类。

图5.10 网络摄像头报错处理

## 5.3 摄像头或视频图像显示的实现

该模块主要功能是显示姿态估计的图像、原始视频帧率、实时视频帧率、视频总时长、视频播放进度、摄像头设备信息的输出，以及搜索、暂停、继续、模型切换、模型加载等按钮功能的实现，UI界面如图5.11所示。

图5.11 摄像头或视频图像显示区域UI

显示摄像头设备的实现原理是当用户点击摄像头设备后，其点击事件的槽函数会发射一个设备信息的信号，当显示摄像头设备的文本框接收到该信号后，先清空该文本框中的内容，然后将接收到的信号再输出到该文本框中。

实现显示原始视频帧率、实时视频帧率、视频总时长、视频播放进度的函数源码如下。

```python
def txt_fond(self, txt_str: str, input_str: object, pose: int = 1, 
                   font: int = cv2.FONT_HERSHEY_COMPLEX_SMALL, 
                   colour: Tuple[int, int, int] = (255, 0, 0),
                   font_thickness: int = 2) -> None):
    txt_0 = txt_str + ":{:.2f}".format(input_str)
    font_scale = min(self.image.shape[1] /640.0, self.image.shape[0] / 480.0) * 0.5 
    text_size = cv2.getTextSize(txt_0, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 2)[0][0]
    cv2.putText(self.image, txt_0, (10,(text_size // 10) * pose), 
                font, font_scale, colour, thickness=font_thickness)

```

搜索按钮的实现：程序先读取显示摄像头设备信息文本框中的内容，然后将其作为参数，传入到实现点击列表视图元素的槽函数上。继续和暂停按钮的实现是通过线程锁控制worker类实现。模型的切换和模型的加载分别是通过模型开关标签self.is_open_moldes 和模型切换标签self.is_DualSwitch控制worker类中run方法执行的分支语句实现的。支持文件拖放到窗口进行人体姿态检测：通过赋值self.setAcceptDrops属性为True，并重写释放鼠标事件的槽函数实现。拖动文件后在窗口上释放文件，会在输入框中显示文件路径或文件URL，该功能是通过调用dropEvent方法实现的，代码如下。

```pytho
self.setAcceptDrops(True)
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()
    def dropEvent(self, event):
        event.acceptProposedAction()
        urls = event.mimeData().urls()
        filepath = urls[0].toLocalFile()
        self.input_txt(filepath)
        self.on_btn_search()
```

## 5.4 日志和雷达视图的实现

日志和雷达视图区域UI界面如图5.12所示，为了使雷达图比例协调，设计了4种情况，分别是当人数为0人、1到3人、3到5人、大于5人等一下是实现代码。

```python
def radar_map(self, lists_data):
body_part_count,average_score,max_count=self.worker.calculate_metrics(lists_data)
angles = np.linspace(0, 2 * np.pi, 3, endpoint=False).tolist() 
values = [int(average_score * 100), body_part_count, max_count * 10] 
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

    self.ax.fill(angles, values,color=set_color, alpha=0.25)
    self.ax.plot(angles, values,color=set_color, linewidth=2)
    labels = ['置信度 (%)', '关键节点数', '人数 (%10)']

    self.ax.set_xticks(angles)
    self.ax.set_xticklabels(labels)
    self.canvas.draw()  # 重新绘制画布以显示更新

```

图5.12 日志和雷达视图

## 5.5 视频和图片列表视图的实现

图5.13和图5.14所示分别为视频列表视图和图片列表视图

图5.13视频列表视图                图5.14 图片列表视图

为了使系统传入的数据为有效的视频或图片数据，在设计列表视图的文件系统模型的时，自动屏蔽了非视频文件后缀或非图片文件后缀的文件，如test.py、test1.docx、test2.docx等文件。点击切换目录时打开操作系统的文件系统，点击选择文件夹，即可实现文件目录的切换，如图5.15

服务器文件列表视图是用来显示网络文件，对于服务器的文件系统的访问，本课题使用Nginx代理服务实现，其原理是利用正则表达是匹配a标签的内容，然后将结果写入到列表中，然后以该列表建立文件系统。服务器文件地址的URL可在config配置文件中自定义，这里对不可访问的URL做了异常处理，如图5.16所示。

   图5.15 切换文件目录                             图5.16  URL异常处理

## 5.6 图片图像显示窗口的实现

图5.17所示为图片姿态估计的显示窗口，本窗口一次性展示5张图片，分别是原图、X轴方向的灰度图、Y轴方向的灰度图、热力图、OpenPose预测图。实现的原理是，当worker类启动图像数据处理后，worker类一次性会发射五个信号，当window类接收到信号后，更新Qlabel上的图像。搜索按钮和数据源输出框的实现跟视频或摄像头模块中搜索按钮和数据源显示的实现方法的类似。

图5.17图片姿态检测显示窗口

## 5.7 修改算法源码

### 5.7.1 增加都网络图片的姿态估计

由于OpenPose源码不支持对网络图片的姿态估计，为了实现本课题的需求，本系统对OpenPose源码做了简单的功能扩展，具体在tf-pose/common.py中增加了server_imgfile函数，修改了read_imgfile函数，其中read_imgfile函数对输入的字符串做了一个判断，当输入的参数Path能被正则表达式'http[s]?://.*\.(jpg|jpeg|png|bmp|gif|tiff)$'匹配到时，则调用server_imgfile函数，该函数使用request库中的get方法对传入的参数Path变量的URL发出请求，当请求成功后，再使用BytesIO方法从HTTP响应中获取图像数据，然后再将图像数据使用opencv读取。增加和修改源码之后的代码如下。

```python
def server_imgfile(path):
    response = requests.get(path)
    if response.status_code == 200:
        image_data = BytesIO(response.content) 
        image = cv2.imdecode(np.frombuffer(image_data.read(), 
                             np.uint8), cv2.IMREAD_UNCHANGED)
        return image

def read_imgfile(path, width=None, height=None):
    val_image = None
    try:
        val_image = cv2.imread(path, cv2.IMREAD_COLOR)
    except:
        pass  # todo
    if re.match(r'http[s]?://.*\.(jpg|jpeg|png|bmp|gif|tiff)$', 
                path, re.IGNORECASE):
        val_image = server_imgfile(path)
    if width is not None and height is not None:
        val_image = cv2.resize(val_image, (width, height))
    return val_image

```

除此之外由于OpenPose源码基于tf1.0版本开发，当系统启动时会有大量的警告，并且在tf2.0以上的版本中OpenPose源码是无法运行的，为了消除警告和tf2.0适配的问题，本系统将OpenPose源码中tf1.0的语法替换成了可兼容tf2.0的语法，并修改了NumPy库中的部分语法。

### 5.7.2 关闭所有OpenPose的调试功能

由于OpenPose源码有大量的调试功能，在运行视频数据的时候会产生大量的日志文件，OpenPose算法在每检测到人体的一个关键节点后就会输出一个日志文件，一般情况下模型处理视频的FPS可达到20帧，若检测视频中只有一个人时，每秒至少也要创建360个文件。这导致了程序在执行一段时间后，模型处理视频的FPS会越来越低甚至导致系统崩溃。原因是OpenPose在运行的时候生成了大量的垃圾文件，产生了大量的磁盘IO，这很大的影响系统的稳定性与图像处理的速度。为了解决问题，本系统关闭了OpenPose输出日志的功能，将关键节点信息的输出显示到了qt的文本框中，但是每秒在qt的文本框中更新360次字符串，对系统的性能也有很大的开销，为了进一步减轻系统的压力，本系统再次优化了获取关键节点信息的逻辑，这里使用到了定时器的功能，系统并没有将每一次检测到的关键节点的信息输出，而是每隔一秒获取一次关键节点信息的方式输出日志，具体的实现分装在run_app/listviow/logging_Qwidget.py模块中，该模块涉及到的核心技术是多线程和定时器。
