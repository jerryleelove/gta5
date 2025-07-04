import cv2
import numpy as np
import pydirectinput
import time
import os
import sys
import ctypes
import win32api
import win32con
import win32gui
from PIL import ImageGrab
from PIL import Image
import matplotlib.pyplot as plt
import psutil
import subprocess
from typing import Optional
import ctypes
from typing import Optional, Tuple

# 初始化设置
pydirectinput.FAILSAFE = False  # 禁用安全暂停
# 请求管理员权限
if not ctypes.windll.shell32.IsUserAnAdmin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

# 图片路径
IMAGE_A = r"C:\Users\Atom\Desktop\code\python\gta5\photo\a.png"
IMAGE_B = r"C:\Users\Atom\Desktop\code\python\gta5\photo\b.png"
IMAGE_C = r"C:\Users\Atom\Desktop\code\python\gta5\photo\c.png"
IMAGE_D = r"C:\Users\Atom\Desktop\code\python\gta5\photo\d.png"
IMAGE_E = r"C:\Users\Atom\Desktop\code\python\gta5\photo\e.png"          # 原dynasty8.png
IMAGE_F = r"C:\Users\Atom\Desktop\code\python\gta5\photo\f.png"          # 原assets.png
IMAGE_G = [r"C:\Users\Atom\Desktop\code\python\gta5\photo\g{}.png".format(i) for i in range(1,7)]  # 保持g1-g6
IMAGE_H = r"C:\Users\Atom\Desktop\code\python\gta5\photo\h.png"          # 原assets.png
IMAGE_I = r"C:\Users\Atom\Desktop\code\python\gta5\photo\i.png"
IMAGE_j = r"C:\Users\Atom\Desktop\code\python\gta5\photo\j.png"
IMAGE_k = r"C:\Users\Atom\Desktop\code\python\gta5\photo\k.png"

# 配置区（可根据需要修改）
EPIC_LAUNCH_PATH = r"C:\Program Files\Epic Games\GTAVEnhanced\PlayGTAV.exe"  # 您的实际路径
GTA_PROCESS_NAME = "GTA5_Enhanced.exe"  # 实际进程名
STEAM_MODE = False  # 如果是Steam版改为True
bat_file = r"C:\Users\Atom\Desktop\GTA.bat"

def bring_to_front(window_title="Grand Theft Auto V"):
    """将游戏窗口强制置顶"""
    try:
        hwnd = win32gui.FindWindow(None, window_title)
        if hwnd:
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.5)
    except:
        pass

def is_image_on_screen(template_path, threshold=0.8):
    """检测图片是否存在"""
    screenshot = np.array(ImageGrab.grab())
    screenshot_cv = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
    template = cv2.imread(template_path)
    if template is None:
        raise ValueError(f"无法读取图片: {template_path}")
    res = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
    return np.max(res) >= threshold


def wait_for_image(image_path, timeout=30, check_interval=0.5):
    """等待图片出现，超时返回False"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if is_image_on_screen(image_path):
            return True
        time.sleep(check_interval)
    return False


def press_key(key, interval=1):
    """按指定键并等待"""
    pydirectinput.press(key)
    print(f"已按 {key.upper()}，等待 {interval}秒")
    time.sleep(interval)


def real_click(button='left'):
    """使用win32api实现真实鼠标点击"""
    if button == 'left':
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
        time.sleep(0.05)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
    elif button == 'right':
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0)
        time.sleep(0.05)
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0)
    elif button == 'middle':
        win32api.mouse_event(win32con.MOUSEEVENTF_MIDDLEDOWN, 0, 0)
        time.sleep(0.05)
        win32api.mouse_event(win32con.MOUSEEVENTF_MIDDLEUP, 0, 0)
    print(f"已点击 鼠标{ '右键' if button == 'right' else '中键' }")
    time.sleep(1)

def execute_final_sequence():
    """最终按键序列"""
    print("执行最终按键序列...")
    press_key('esc', 1)
    for i in range(5):
        press_key('e', 1)
    press_key('enter', 1)
    press_key('w', 1)
    press_key('enter', 1)
    press_key('s', 1)
    press_key('enter', 1)
    press_key('enter', 1)
    print("基础按键操作完成！")

def mouse_scroll(clicks=3, direction='down'):
    """模拟鼠标滚轮滚动"""
    for _ in range(clicks):
        if direction == 'down':
            win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, -120, 0)  # 向下滚动
        else:
            win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, 120, 0)   # 向上滚动
        time.sleep(0.3)
    print(f"鼠标滚轮向{'下' if direction == 'down' else '上'}滚动{clicks}次")


def handle_image_c_and_d():
    """处理图片C和D的逻辑"""
    bring_to_front()  # 确保游戏窗口在前台

    print("等待online画面(图片C)出现...")
    if not wait_for_image(IMAGE_C, timeout=30):
        print("错误：online画面未在30秒内出现！")
        return

    print("监控online画面，等待其消失...")
    while is_image_on_screen(IMAGE_C):
        time.sleep(0.5)

    print("online画面已消失，等待3秒...")
    time.sleep(3)

    print("检测phone画面(图片D)...")
    if is_image_on_screen(IMAGE_D):
        real_click('right')
    else:
        real_click('middle')
        time.sleep(1)
        mouse_scroll(3, 'down')
        time.sleep(1)
        real_click('left')
        time.sleep(1)

def click_at_image(image_path, timeout=10, click_delay=1):
    """识别并点击图片中心位置"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        screenshot = np.array(ImageGrab.grab())
        screenshot_cv = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
        template = cv2.imread(image_path)

        if template is None:
            raise ValueError(f"无法读取图片: {image_path}")

        res = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        if max_val > 0.8:  # 匹配阈值
            h, w = template.shape[:-1]
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2

            # # 创建可视化图像
            # fig, ax = plt.subplots(figsize=(10, 6))
            # ax.imshow(ImageGrab.grab())
            #
            # # 标记识别区域
            # rect = plt.Rectangle((max_loc[0], max_loc[1]), w, h,
            #                      linewidth=2, edgecolor='lime', facecolor='none')
            # ax.add_patch(rect)
            # ax.set_title(f'识别到: {os.path.basename(image_path)}\n相似度: {max_val:.2f}')
            # plt.axis('off')

            # # 非阻塞显示（3秒后自动关闭）
            # plt.show(block=False)
            # plt.pause(1)

            # 移动并点击
            pydirectinput.moveTo(center_x, center_y)
            # time.sleep(0.2)
            real_click('left')
            print(f"已点击图片: {os.path.basename(image_path)}")
            # time.sleep(click_delay)
            return True

    print(f"未找到图片: {os.path.basename(image_path)} (超时: {timeout}秒)")
    return False

def process_image_sequence():
    """处理图片E到G6的识别点击流程"""
    # 处理图片E
    if not click_at_image(IMAGE_E):
        return

    # 处理图片F
    if not click_at_image(IMAGE_F):
        return

    # 处理G1-G6图片
    for g_path in IMAGE_G:
        if not click_at_image(g_path):
            break
        # time.sleep(1)

    if not click_at_image(IMAGE_H):
        return

    if not click_at_image(IMAGE_I):
        return
    time.sleep(1)
    press_key('enter', 1)
    time.sleep(1)
    press_key('enter', 1)
    time.sleep(1)
    os.system(f'"{bat_file}"')

def main():

    print("=== GTA5 自动按键脚本（online等待3秒版）===")
    print("3秒内切换到游戏窗口...")
    time.sleep(3)

    try:
        # 第一阶段：原有操作
        print("等待开始按钮(图片A)出现...")
        if not wait_for_image(IMAGE_A, timeout=30):
            print("错误：开始按钮未在30秒内出现！")
            return

        print("检测到开始按钮，正在按 E、E、Enter...")
        for _ in range(2):
            press_key('e', 1)
        press_key('enter', 1)

        # 第二阶段：b.png处理
        print("等待b画面(图片B)出现...")
        if not wait_for_image(IMAGE_B, timeout=30):
            print("错误：b画面未在30秒内出现！")
            return

        print("监控b画面，等待其消失...")
        while is_image_on_screen(IMAGE_B):
            time.sleep(0.5)

        print("b画面已消失，等待3秒...")
        time.sleep(3)

        print("开始执行最终按键序列...")
        execute_final_sequence()

        # 第三阶段：c.png和d.png处理
        handle_image_c_and_d()

        process_image_sequence()

    except KeyboardInterrupt:
        print("\n脚本已手动停止")
    except Exception as e:
        print(f"发生错误: {str(e)}")


if __name__ == "__main__":
    image_paths = [IMAGE_A, IMAGE_B, IMAGE_C, IMAGE_D]
    if not all(os.path.exists(p) for p in image_paths):
        print("错误：图片路径不存在！")
        for i, path in enumerate(image_paths):
            print(f"图片{'ABCD'[i]}({os.path.basename(path)})是否存在: {'是' if os.path.exists(path) else '否'}")
    else:
        main()