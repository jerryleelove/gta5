import cv2
import numpy as np
import pytesseract
import pyautogui
import time


# 配置Tesseract路径（如果需要）
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def preprocess_image(image, target_height=30):
    """自动调整文字大小至理想高度(默认30像素)"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 计算当前文字高度（通过连通域分析）
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        avg_height = np.mean([cv2.boundingRect(cnt)[3] for cnt in contours])
        scale = target_height / avg_height
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    # 继续原有处理流程
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 11, 2)
    return thresh

def monitor_screen_for_text(target_text, lang='eng', region=None, interval=1, confidence=70):
    """
    监控屏幕直到找到目标文字
    :param target_text: 要查找的文字
    :param lang: 语言代码(默认英文)
    :param region: (left, top, width, height)监控区域，None为全屏
    :param interval: 检查间隔(秒)
    :param confidence: 置信度阈值(0-100)
    """
    print(f"开始监控屏幕，寻找文字: '{target_text}'...")
    print("按下Ctrl+C停止监控")

    try:
        while True:
            # 1. 截取屏幕
            screenshot = pyautogui.screenshot(region=region)
            img = np.array(screenshot)

            # 2. 图像预处理
            processed_img = preprocess_image(img)

            # 3. 使用Tesseract识别文字
            data = pytesseract.image_to_data(
                processed_img,
                lang=lang,
                output_type=pytesseract.Output.DICT
            )

            # 4. 检查是否找到目标文字
            found = False
            for i, text in enumerate(data['text']):
                if text.strip() and target_text.lower() in text.lower():
                    if int(data['conf'][i]) >= confidence:
                        print(f"找到文字 '{text}' (置信度: {data['conf'][i]}%)")
                        x = data['left'][i] + data['width'][i] // 2
                        y = data['top'][i] + data['height'][i] // 2
                        if region:  # 调整坐标到全屏位置
                            x += region[0]
                            y += region[1]
                        print(f"位置: ({x}, {y})")
                        found = True
                        break

            if found:
                break

            time.sleep(interval)

    except KeyboardInterrupt:
        print("\n监控已停止")
    except Exception as e:
        print(f"发生错误: {e}")


# 使用示例
if __name__ == "__main__":
    # 参数配置
    TARGET_TEXT = "GTA"  # 要查找的文字
    LANGUAGE = "eng"  # 英语
    MONITOR_REGION = None  # 监控区域(left, top, width, height)
    CHECK_INTERVAL = 1  # 检查间隔(秒)
    CONFIDENCE_LEVEL = 70  # 置信度阈值

    # 开始监控
    monitor_screen_for_text(
        target_text=TARGET_TEXT,
        lang=LANGUAGE,
        region=MONITOR_REGION,
        interval=CHECK_INTERVAL,
        confidence=CONFIDENCE_LEVEL
    )