import base64

import cv2
import fitz
import numpy as np


class PdfImgConversion:
    def __init__(self):
        self.dpi = 216  # DPI每英寸点数, 1点等于1/72英寸, 72是DPI到pt的转换因子
        self.x_scale = 3  # dpi / 72
        self.y_scale = 3

    def page_to_img(self, page):
        mat = fitz.Matrix(self.x_scale, self.y_scale)  # 定义坐标变换的矩阵
        pix = page.get_pixmap(matrix=mat, alpha=False)  # alpha=False去除透明度，如果不需要的话
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape((pix.height, pix.width, pix.n))
        if pix.n == 4:  # RGBA
            img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGRA)
        elif pix.n == 3:  # RGB
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        elif pix.n == 1:  # Grayscale
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        return img

    def scale_up_bbox(self, x1, y1, x2, y2):
        return x1 * self.x_scale, y1 * self.y_scale, x2 * self.x_scale, y2 * self.y_scale

    def scale_down_bbox(self, x1, y1, x2, y2):
        return x1 / self.x_scale, y1 / self.y_scale, x2 / self.x_scale, y2 / self.y_scale


def image_to_base64(image):
    """
    将OpenCV图像转换为Base64编码的字符串。

    参数:
    image (numpy.ndarray): OpenCV图像（np.array格式）。

    返回:
    str: Base64编码的图像字符串。
    """
    # # 将图像从OpenCV的BGR格式转换为RGB格式（如果需要显示在网页上）
    # image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    #
    # # 创建一个BytesIO对象作为内存缓冲区
    # buffer = BytesIO()
    #
    # # 将图像保存到内存缓冲区中，格式可以是JPEG、PNG等，这里以JPEG为例
    # image_rgb.save(buffer, format='JPEG')
    # cv2.imwrite('./a.jpeg', image)
    # # 获取内存缓冲区的二进制数据
    # img_bytes = buffer.getvalue()
    _, img_bytes = cv2.imencode('.jpeg', image)  # 使用imencode直接将图像编码为字节
    # 对二进制数据进行Base64编码
    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
    # print("data:image/jpeg;base64," + img_base64)
    return "data:image/jpeg;base64," + img_base64


def basse64_img_save(base64_data, file_url):
    b64_data = base64_data.split(';base64,')[1]
    data = base64.b64decode(b64_data)
    with open(file_url, 'wb') as f:
        f.write(data)
