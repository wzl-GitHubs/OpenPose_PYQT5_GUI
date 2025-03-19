from enum import Enum
import re
import requests
from io import BytesIO
import numpy as np
import tensorflow as tf
import cv2

regularizer_conv = 0.004
regularizer_dsconv = 0.0004
batchnorm_fused = True
activation_fn = tf.nn.relu


class CocoPart(Enum):
    Nose = 0
    Neck = 1
    RShoulder = 2
    RElbow = 3
    RWrist = 4
    LShoulder = 5
    LElbow = 6
    LWrist = 7
    RHip = 8
    RKnee = 9
    RAnkle = 10
    LHip = 11
    LKnee = 12
    LAnkle = 13
    REye = 14
    LEye = 15
    REar = 16
    LEar = 17
    Background = 18


class MPIIPart(Enum):
    RAnkle = 0
    RKnee = 1
    RHip = 2
    LHip = 3
    LKnee = 4
    LAnkle = 5
    RWrist = 6
    RElbow = 7
    RShoulder = 8
    LShoulder = 9
    LElbow = 10
    LWrist = 11
    Neck = 12
    Head = 13

    @staticmethod
    def from_coco(human):
        # t = {
        #     MPIIPart.RAnkle: CocoPart.RAnkle,
        #     MPIIPart.RKnee: CocoPart.RKnee,
        #     MPIIPart.RHip: CocoPart.RHip,
        #     MPIIPart.LHip: CocoPart.LHip,
        #     MPIIPart.LKnee: CocoPart.LKnee,
        #     MPIIPart.LAnkle: CocoPart.LAnkle,
        #     MPIIPart.RWrist: CocoPart.RWrist,
        #     MPIIPart.RElbow: CocoPart.RElbow,
        #     MPIIPart.RShoulder: CocoPart.RShoulder,
        #     MPIIPart.LShoulder: CocoPart.LShoulder,
        #     MPIIPart.LElbow: CocoPart.LElbow,
        #     MPIIPart.LWrist: CocoPart.LWrist,
        #     MPIIPart.Neck: CocoPart.Neck,
        #     MPIIPart.Nose: CocoPart.Nose,
        # }

        t = [
            # MPII数据集的头部对应Coco数据集的鼻子
            (MPIIPart.Head, CocoPart.Nose),
            # MPII数据集的颈部对应Coco数据集的颈部
            (MPIIPart.Neck, CocoPart.Neck),
            # MPII数据集的右肩对应Coco数据集的右肩
            (MPIIPart.RShoulder, CocoPart.RShoulder),
            # MPII数据集的右肘对应Coco数据集的右肘
            (MPIIPart.RElbow, CocoPart.RElbow),
            # MPII数据集的右腕对应Coco数据集的右腕
            (MPIIPart.RWrist, CocoPart.RWrist),
            # MPII数据集的左肩对应Coco数据集的左肩
            (MPIIPart.LShoulder, CocoPart.LShoulder),
            # MPII数据集的左肘对应Coco数据集的左肘
            (MPIIPart.LElbow, CocoPart.LElbow),
            # MPII数据集的左腕对应Coco数据集的左腕
            (MPIIPart.LWrist, CocoPart.LWrist),
            # MPII数据集的右髋对应Coco数据集的右髋
            (MPIIPart.RHip, CocoPart.RHip),
            # MPII数据集的右膝对应Coco数据集的右膝
            (MPIIPart.RKnee, CocoPart.RKnee),
            # MPII数据集的右踝对应Coco数据集的右踝
            (MPIIPart.RAnkle, CocoPart.RAnkle),
            # MPII数据集的左髋对应Coco数据集的左髋
            (MPIIPart.LHip, CocoPart.LHip),
            # MPII数据集的左膝对应Coco数据集的左膝
            (MPIIPart.LKnee, CocoPart.LKnee),
            # MPII数据集的左踝对应Coco数据集的左踝
            (MPIIPart.LAnkle, CocoPart.LAnkle),
        ]

        pose_2d_mpii = []
        visibilty = []
        for mpi, coco in t:
            if coco.value not in human.body_parts.keys():
                pose_2d_mpii.append((0, 0))
                visibilty.append(False)
                continue
            pose_2d_mpii.append((human.body_parts[coco.value].x, human.body_parts[coco.value].y))
            visibilty.append(True)
        return pose_2d_mpii, visibilty


# Coco数据集中的骨骼关键点连接对
CocoPairs = [
    # 头部
    (1, 2), (1, 5),
    # 右臂
    (2, 3), (3, 4),
    # 左臂
    (5, 6), (6, 7),
    # 躯干
    (1, 8), (8, 9), (9, 10),
    # 右腿
    (1, 11), (11, 12), (12, 13),
    # 左腿
    (1, 0), (0, 14), (14, 16),
    # 右腿
    (0, 15), (15, 17),
    # 右臂与躯干连接
    (2, 16),
    # 左臂与躯干连接
    (5, 17)
]  # 总共19个连接对
CocoPairsRender = CocoPairs[:-2]
# Coco数据集的骨骼关键点颜色
CocoColors = [
    [255, 0, 0],  # 红色
    [255, 85, 0],  # 橙色
    [255, 170, 0],  # 黄色
    [255, 255, 0],  # 绿色
    [170, 255, 0],  # 青色
    [85, 255, 0],  # 浅绿色
    [0, 255, 0],  # 蓝色
    [0, 255, 85],  # 紫色
    [0, 255, 170],  # 天蓝色
    [0, 255, 255],  # 浅蓝色
    [0, 170, 255],  # 靛蓝色
    [0, 85, 255],  # 深紫色
    [0, 0, 255],  # 深蓝色
    [85, 0, 255],  # 紫色
    [170, 0, 255],  # 靛蓝色
    [255, 0, 255],  # 粉红色
    [255, 0, 170],  # 紫红色
    [255, 0, 85]  # 红色
]


# CocoPairs = [
#     (1, 2), (1, 5), (2, 3), (3, 4), (5, 6), (6, 7), (1, 8), (8, 9), (9, 10), (1, 11),
#     (11, 12), (12, 13), (1, 0), (0, 14), (14, 16), (0, 15), (15, 17), (2, 16), (5, 17)
# ]  # = 19
# CocoPairsRender = CocoPairs[:-2]
# # CocoPairsNetwork = [
# #     (12, 13), (20, 21), (14, 15), (16, 17), (22, 23), (24, 25), (0, 1), (2, 3), (4, 5),
# #     (6, 7), (8, 9), (10, 11), (28, 29), (30, 31), (34, 35), (32, 33), (36, 37), (18, 19), (26, 27)
# #  ]  # = 19
#
# CocoColors = [[255, 0, 0], [255, 85, 0], [255, 170, 0], [255, 255, 0], [170, 255, 0], [85, 255, 0], [0, 255, 0],
#               [0, 255, 85], [0, 255, 170], [0, 255, 255], [0, 170, 255], [0, 85, 255], [0, 0, 255], [85, 0, 255],
#               [170, 0, 255], [255, 0, 255], [255, 0, 170], [255, 0, 85]]


def server_imgfile(path):
    """
    网络图片的读取
    :param path:url
    :return:图像数据
    """
    response = requests.get(path)
    if response.status_code == 200:  # 确保请求成功
        image_data = BytesIO(response.content)  # 从HTTP响应中获取图像数据
        image = cv2.imdecode(np.frombuffer(image_data.read(), np.uint8), cv2.IMREAD_UNCHANGED)
        return image


def read_imgfile(path, width=None, height=None):
    """
    读取本地或网络图片数据的函数
    :param path: 文件的地址
    :param width: 长
    :param height: 宽
    :return: 图像数据
    """
    val_image = None
    try:
        val_image = cv2.imread(path, cv2.IMREAD_COLOR)
    except:
        pass  # todo
    if re.match(r'http[s]?://.*\.(jpg|jpeg|png|bmp|gif|tiff)$', path, re.IGNORECASE):
        val_image = server_imgfile(path)
    if width is not None and height is not None:
        val_image = cv2.resize(val_image, (width, height))
    return val_image


def get_sample_images(w, h):
    val_image = [
        read_imgfile('./images/p1.jpg', w, h),
        read_imgfile('./images/p2.jpg', w, h),
        read_imgfile('./images/p3.jpg', w, h),
        read_imgfile('./images/golf.jpg', w, h),
        read_imgfile('./images/hand1.jpg', w, h),
        read_imgfile('./images/hand2.jpg', w, h),
        read_imgfile('./images/apink1_crop.jpg', w, h),
        read_imgfile('./images/ski.jpg', w, h),
        read_imgfile('./images/apink2.jpg', w, h),
        read_imgfile('./images/apink3.jpg', w, h),
        read_imgfile('./images/handsup1.jpg', w, h),
        read_imgfile('./images/p3_dance.png', w, h),
    ]
    return val_image
