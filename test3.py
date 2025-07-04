import cv2
import numpy as np
import pytesseract
import pyautogui
import time
import re
from pynput.keyboard import Controller

# 初始化Tesseract路径（根据实际安装位置修改）
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# 初始化键盘控制器
keyboard = Controller()


def auto_resize_text(image, target_height=30):
    """
    动态调整文字大小到最佳识别尺寸
    :param image: 输入图像(numpy数组)
    :param target_height: 目标文字高度(像素)
    :return: 处理后的图像
    """
    # 转为灰度图
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 初步二值化找文字轮廓
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        # 计算平均文字高度
        heights = [cv2.boundingRect(cnt)[3] for cnt in contours if cv2.boundingRect(cnt)[3] > 5]  # 过滤噪点
        if heights:
            avg_height = np.mean(heights)
            scale = target_height / avg_height

            # 应用缩放（限制缩放范围避免极端情况）
            scale = max(0.5, min(2.0, scale))  # 限制在0.5-2倍之间
            resized = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
            return resized

    return gray  # 默认返回原灰度图


def preprocess_image(image):
    """
    完整的图像预处理流程
    :param image: 输入图像(numpy数组)
    :return: 优化后的二值图像
    """
    # 步骤1：自动调整文字大小
    resized = auto_resize_text(image)

    # 步骤2：自适应阈值
    thresh = cv2.adaptiveThreshold(resized, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 11, 2)

    # 步骤3：降噪处理
    kernel = np.ones((2, 2), np.uint8)
    processed = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)

    # 步骤4：边缘增强
    processed = cv2.bilateralFilter(processed, 9, 75, 75)

    return processed


def contains_digits(image):
    """
    检测图像中是否包含数字
    :param image: 输入图像
    :return: bool
    """
    processed = preprocess_image(image)
    custom_config = r'--oem 3 --psm 6 outputbase digits'
    text = pytesseract.image_to_string(processed, config=custom_config)
    return bool(re.search(r'\d', text))


def execute_gta_sequence():
    """
    执行GTA+操作序列
    :return: bool 是否执行成功
    """
    print("\n执行操作序列...")
    try:
        # 第一次按E
        time.sleep(1)
        pyautogui.press('e')
        print("已按下: E")

        # 第二次按E
        time.sleep(1)
        pyautogui.press('e')
        print("已按下: E")

        # 按Enter
        time.sleep(1)
        pyautogui.press('enter')
        print("已按下: Enter")

        # 检测数字
        print("检测数字中...")
        for _ in range(10):  # 最多检测10次（5秒）
            screenshot = np.array(pyautogui.screenshot())
            if contains_digits(screenshot):
                time.sleep(1)
                pyautogui.press('esc')
                print("检测到数字，已按下: Esc")
                return True
            time.sleep(0.5)

        print("未检测到数字")
        return False

    except Exception as e:
        print(f"操作执行出错: {str(e)}")
        return False


def detect_gta_plus(image):
    """
    检测图像中是否包含GTA+
    :param image: 输入图像
    :return: bool
    """
    processed = preprocess_image(image)

    # 多尺度检测配置
    scales = [0.9, 1.0, 1.1] if image.shape[0] > 1000 else [0.8, 1.0, 1.2]

    for scale in scales:
        try:
            # 缩放图像
            resized = cv2.resize(processed, None, fx=scale, fy=scale)

            # 识别文字
            data = pytesseract.image_to_data(
                resized,
                lang='eng',
                config='--psm 6 --oem 3',
                output_type=pytesseract.Output.DICT
            )

            # 检查GTA+
            for i, text in enumerate(data['text']):
                text_upper = text.upper().strip()
                if ('GTA+' in text_upper or 'GTA +' in text_upper) and int(data['conf'][i]) > 65:
                    print(f"检测到GTA+ (置信度: {data['conf'][i]}%, 缩放: {scale}x)")
                    return True

        except Exception as e:
            continue

    return False


def main_loop():
    """主监控循环"""
    print("GTA+自动化监控已启动 (Ctrl+C退出)")
    cooldown = 0  # 操作冷却计时器

    try:
        while True:
            if cooldown <= 0:
                # 截屏并检测
                screenshot = np.array(pyautogui.screenshot())
                if detect_gta_plus(screenshot):
                    if execute_gta_sequence():
                        cooldown = 10  # 成功操作后冷却10秒
                    else:
                        cooldown = 5  # 失败后冷却5秒
            else:
                cooldown -= 1
                time.sleep(1)
                continue

            time.sleep(0.5)  # 检测间隔

    except KeyboardInterrupt:
        print("\n监控已手动停止")
    except Exception as e:
        print(f"程序出错: {str(e)}")


if __name__ == "__main__":
    # 检查依赖
    try:
        pytesseract.get_tesseract_version()
    except EnvironmentError:
        print("错误: Tesseract未正确安装或配置")
        exit(1)

    # 启动主循环
    main_loop()
    print("程序已退出")