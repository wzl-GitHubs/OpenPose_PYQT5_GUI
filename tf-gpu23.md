### 一、TF-GUP版安装

![png](E:\tf-pose\resources\images\test31.jpg)

下载安装andconda或minconda

推荐minconda 因为小巧，andconda集成库太多并且内置的numpy pandas matplotlib的版本与tensorflow不适配。需要在虚拟环境重新安装numpy pandas matplotlib

minconda官网链接

[Miniconda — conda documentation](https://docs.conda.io/en/latest/miniconda.html)

下载链接

https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe

安装时选择给所有用户安装然后继续选择添加环境变量点击安装即可。由于过于简单不予赘述。

#### 更换conda pip 下载镜像源

需要说明的是下面的操作同样适合Linux平台。本人已经在Ubuntu22.04版本成功安装。

这里我只以Windows系统举例。

##### conda更换镜像源

cmd输入

```shell
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --set show_channel_urls yes
```

##### pip换源

pip config set global.index-url [+源地址]

清华大学：https://pypi.tuna.tsinghua.edu.cn/simple
阿里云：http://mirrors.aliyun.com/pypi/simple/
中国科技大学: https://pypi.mirrors.ustc.edu.cn/simple/
华中理工大学：http://pypi.hustunique.com/
山东理工大学：http://pypi.sdutlinux.org/
豆瓣：http://pypi.douban.com/simple/
网易：http://mirrors.163.com

```shell
例如换成阿里云源则需要执行：
pip config set global.index-url http://mirrors.aliyun.com/pypi/simple/
```

#### 下载tensorflow

##### 1、创建虚拟环境

```python
conda create -n tf-gpu2.3 Python= 3.7.6
```

-n:自定义的虚拟环境名，我的虚拟环境为tf-gpu2.3； 

python版本，选择python 3.7；

##### 2、激活已创建好的虚拟环境，命令行输入：

```python
conda activate tf-gpu2.3
```

注意下面的操作一定实在刚激活的虚拟环境中进行的不要关闭终端

##### 3、命令一：用于检查当前的cuda版本号

安装对应的cuda与cudnn版本，注意不用预装cuda和cudnn安装包，有你卡驱动就行
参考官网

https://tensorflow.google.cn/install/source_windows?hl=zh-cn

其实3、4可以省略，就按的的配置往下敲，因为我只找到了一个GPU版本Tensorflow可兼容pands numpy的版本，不必和我一样浪费时间和经历。直接可以看5、但是我想让你知道科学的安装过程，并不是教你去下载整个n卡的软件。一定要掌握原理

```shell
conda search cuda
```

##### 4、命令二：用于检查当前的cudnn版本号

```python
conda search cudnn
```

##### 5、确定版本型号搭配

cudatoolkit=10.1    cudnn=7.6.5  tensorflow-gpu==2.3.0

##### 6、下载安装

```shell
conda install -c conda-forge cudatoolkit=10.1.243 cudnn=7.6.5
```

```python
conda install cudatoolkit=10.1
conda install cudnn=7.6.5
pip install tensorflow-gpu==2.3.0 -i https://pypi.douban.com/simple/
```

#### 测试

在虚拟环境中输入python回车

输入以下代码

```python
import tensorflow as tf
tensorflow_version = tf.__version__
gpu_available = tf.test.is_gpu_available()
print('tensorflow version:',tensorflow_version, '\tGPU available:', gpu_available)
a = tf.constant([1.0, 2.0], name='a')
b = tf.constant([1.0, 2.0], name='b')
result = tf.add(a,b, name='add')
print(result)
```

如果有true说明成功安装了恭喜你，少走了很多弯路。输入
exit() # 退出python环境再次进入虚拟环境。

接下来我们安装几个tf常用的几个包，注意下面的版本只适配tensorflow-gpu==2.3.0

#### 四、安装适配库

一条一条的执行

```python
conda install numpy==1.18.5
pip install matplotlib==3.3.3
conda install seaborn==0.9.0
conda install pandas==1.1.5
conda install scikit-learn==0.24.2
conda install ipykernel
```

恭喜你安装完成了，成功走到深度学习的山前。如果你不是追求完美的人。后面的东西可以不看，因为不是必须的。

#### 报错

你可能在使用过程中有以下报错先把我的文档收藏了以便以后用到，我希望你没有报错。

1 报错1KImportError: DLL load failed: 找不到指定的模块。
安装vc++2015-2019

2 TypeError: Descriptors cannot not be created directly（局部错误）
pip install protobuf==3.19.6

3 Could not load dynamic library cudart64_101.dll（局部）
下载cudart64_101.dll文件

pip install cudart64_101.dll

### 二， 配置notebook

我们的目的是实现在notebook创建新的python文件时可以在点击new后直接启动tf的内核。

也就是说不管你是点击的conda的jupyter notebook还是点击tf的 jupyter notebook都可以启动TF的内核。希望你是懂的，不过不懂也没关系。跟着我的思路往下吧。

#### 1.在notebook中添加虚拟环境内核

```shell
python -m ipykernel install --user --name 环境名称 --display-name 环境名称
# 例如我的环境tf-gpu2.3
python -m ipykernel install --user --name tf-gpu2.3 --display-name tf-gpu2.3
```

#### 2.配置默认打开的路径

我们的目的是点击jupyter notebook的快捷键后打开的是我们想进入的目录。

###### <1>  生成jupyter notebook配置文件jupyter_notebook_config.py并打印路径.

输入

```shell
jupyter notebook --generate-config
```

生成jupyter_notebook_config.py文件

（windows的路径：c:\user\用户名.jupyter\jupyter_notebook_config.py）

###### <2> 记事本打开jupyter_notebook_config.py文件

粘贴以下内容

注意windows是反斜杠(\\)，linux是斜杠(/)

```shell
c.NotebookApp.notebook_dir ='你要打开的路径名'# Windows例如C:\user\文档    
c.NotebookApp.use_redirect_file = False # 禁用重定向生成html文件
```

如果你跟着我的思路往下走了，你会发现 （四、安装适配库）的最后一条命令根本不用执行。如果你能懂这一点，说明你理解虚拟环境是怎么一回事了。

#### 3.linux配置桌面快捷方式

Windows用户跳过

##### 一、桌面文件的配置

在 Ubuntu gnome 桌面环境下，桌面文件的后缀名一般为 .desktop，因此，我们首先创建相关桌面文件。

1. ###### 创建桌面文件 jupyter.desktop
   
   桌面右击，打开终端
   
   ```shell
   touch jupyter.desktop
   ```

2. ###### 配置相关桌面文件
   
   使用 vim 打开文件 jupyter.desktop  
   vim jupyter.desktop
   
   复制以下代码进文件
   
   ```shell
   [Desktop Entry]
   Name=Jupyter
   Comment=Open Jupyter Notebook
   Exec=/home/你的用户名/anaconda3/bin/jupyter-notebook
   Icon=/usr/share/applications/jupyter.svg
   Terminal=false
   Type=Application
   Categories=Developer;
   ```

按esc 输入 :wq，保存并退出

```
注：这里的 
Exec 的值为你的 jupyter文件的绝对路径，
Icon 的值为你的图标文件的绝对路径，若完全按照上述步骤操作的话则无需更改。
Terminal=ture参数可以展示命令行
```

3. ###### 配置图标

对于桌面快捷方式和应用图标的文件选择，一般选用矢量图，即后缀名为 .svg 的图片文件

这个呢我们可以在阿里的矢量图库里免费找寻自己喜欢的矢量图，网址如下： 

https://www.iconfont.cn/home/index?spm=a313x.7781069.1998910419.2

进入到下载图标的目录下

右击->选择在终端中打开->键入以下命令，拷贝该图片到系统图标目录下：

```shell
sudo cp jupyter.svg /usr/share/applications
```

jupyter.svg代表你的图标名称

到此图标的配置已经完成

###### 4.设置可执行权限

回到 jupyter.desktop 文件目录下（桌面）

右击->终端中打开，键入如下命令，给桌面文件设置相关可执行权限：

```shell
sudo chmod u+x jupyter.desktop
到这里，桌面文件的相关配置就完毕了。
```

##### 二、配置桌面快捷方式和应用图标

1. ###### 桌面快捷方式的配置
   
   如果上面的4没有执行，请按下面操作
   
   我们在桌面上已经可以看到对应的文件了，但是还是不能运行，需要我们进行进一步操作：
   右键桌面上的文件 >> Allow Launching
   
   可以发现它已经出现了快捷方式的角标图案了，双击，我们便可以成功运行 jupyter 了！

2. ###### 应用图标的配
   
   置在 jupyter.desktop 文件目录下(即桌面)
   打开终端，键入以下命令，将桌面文件放入系统图标文件夹中：
   
   ```shell
   sudo cp jupyter.desktop /usr/share/applications
   ```
   
   打开桌面图标界面，我们便可以在界面中找到 jupyter
   接着右键 jupyter 图标，选择 Add to Favotires
   我们便能在我们的 Dock 中快速打开 jupyter 了 
