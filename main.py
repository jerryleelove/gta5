import cv2
import numpy as np
import pytesseract
import pyautogui
import time
import re
from pynput.keyboard import Controller  # 添加这行导入语句

# 设置Tesseract路径（根据实际安装位置修改）
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def preprocess_image(image):
    """优化图像以提高OCR识别率"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 11, 2)
    kernel = np.ones((2, 2), np.uint8)
    processed = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
    return processed


def contains_digits(image):
    """检测图像中是否包含数字"""
    processed = preprocess_image(image)
    custom_config = r'--oem 3 --psm 6 outputbase digits'
    text = pytesseract.image_to_string(processed, config=custom_config)
    return bool(re.search(r'\d', text))


def execute_gta_sequence():
    """执行完整的GTA+操作流程"""
    print("启动GTA+自动化流程...")

    # 按两次e键
    time.sleep(1)
    pyautogui.press('e')
    print("已按下: e")
    time.sleep(1)
    pyautogui.press('e')
    print("已按下: e")

    # 按一次Enter键
    time.sleep(1)
    pyautogui.press('enter')
    print("已按下: Enter")

    # 检测数字
    print("正在检测数字...")
    for _ in range(20):  # 最多检测10次（5秒）
        screenshot = pyautogui.screenshot()
        img = np.array(screenshot)

        if contains_digits(img):
            print("检测到数字，1秒后按下Esc")
            time.sleep(1)
            pyautogui.press('esc')
            print("已按下: Esc")
            return True

        time.sleep(0.5)

    print("未检测到数字")
    return False


def monitor_for_gta_plus():
    """全屏监控GTA+文字"""
    print("开始全屏监控GTA+...")
    print("按下Ctrl+C可随时终止")

    try:
        while True:
            # 全屏截图
            screenshot = pyautogui.screenshot()
            img = np.array(screenshot)

            # 图像处理
            processed = preprocess_image(img)

            # 识别文字
            data = pytesseract.image_to_data(
                processed,
                lang='eng',
                output_type=pytesseract.Output.DICT
            )

            # 检查GTA+
            for i, text in enumerate(data['text']):
                if 'GTA+' in text.upper() and int(data['conf'][i]) > 50:
                    print(f"发现GTA+ (置信度: {data['conf'][i]}%)")
                    execute_gta_sequence()
                    return

            time.sleep(1)

    except KeyboardInterrupt:
        print("\n监控已手动停止")
    except Exception as e:
        print(f"发生错误: {str(e)}")


if __name__ == "__main__":
    # 开始监控
    monitor_for_gta_plus()
    print("自动化流程执行完毕")