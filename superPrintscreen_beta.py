import os
import time
from PIL import ImageGrab
import keyboard
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import pyperclip
import pyautogui
import threading

# 配置参数
SCREENSHOT_DIR = os.path.abspath("../screenshots")  # 截图保存目录，使用绝对路径防止路径遍历
HOTKEY = "ctrl+alt+q"  # 截图快捷键
LEFT = 0
UP = 0
RIGHT = 2559
DOWN = 1599
REGION = (LEFT, UP, RIGHT, DOWN)  # 截图区域 (左, 上, 右, 下)
UPDATE_INTERVAL = 100  # 鼠标信息更新间隔（毫秒）
NOTIFICATION_DURATION = 2000  # 通知持续时间（毫秒）

# 新增快捷键定义
HOTKEY_COPY_POSITION = "ctrl+alt+shift+a"  # 复制坐标
HOTKEY_COPY_COLOR = "ctrl+alt+shift+s"  # 复制颜色
HOTKEY_COPY_ALL = "ctrl+alt+shift+d"  # 全部复制
HOTKEY_COPY_X = "ctrl+alt+shift+z"  # 复制X值
HOTKEY_COPY_Y = "ctrl+alt+shift+x"  # 复制Y值
HOTKEY_COPY_R = "ctrl+alt+shift+c"  # 复制R值
HOTKEY_COPY_G = "ctrl+alt+shift+v"  # 复制G值
HOTKEY_COPY_B = "ctrl+alt+shift+b"  # 复制B值

# 主题颜色定义
PRIMARY_COLOR = "#3498db"
SECONDARY_COLOR = "#2c3e50"
ACCENT_COLOR = "#e74c3c"
BACKGROUND_COLOR = "#f8f9fa"
LIGHT_BACKGROUND = "#ffffff"
TEXT_COLOR = "#2c3e50"
LIGHT_TEXT = "#7f8c8d"
BUTTON_COLORS = {
    "capture": "#4CAF50",  # 绿色 - 截图
    "fullscreen": "#9C27B0",  # 紫色 - 全屏
    "save": "#2196F3",  # 蓝色 - 保存
    "exit": "#f44336",  # 红色 - 退出
    "preview": "#9C27B0",  # 紫色 - 预览
    "drag": "#FF9800",  # 橙色 - 拖拽
    "browse": "#607D8B",  # 灰蓝 - 浏览
    "copy": "#4CAF50",  # 绿色 - 复制
    "rgb": "#2196F3",  # 蓝色 - RGB
    "all": "#FF9800",  # 橙色 - 全部
    "single": "#BDBDBD",  # 灰色 - 单值
    "shortcut": "#795548"  # 棕色 - 快捷键
}


def save_screenshot(screenshot_img, prefix):
    """保存截图到文件的通用函数"""
    # 确保目录存在
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    # 生成带时间戳的文件名
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"{prefix}_{timestamp}.png"
    filepath = os.path.join(SCREENSHOT_DIR, filename)

    # 保存截图
    screenshot_img.save(filepath)
    print(f"截图已保存至: {filepath}")
    return filepath


def show_system_notification(title, message, filepath):
    """显示系统通知，如果win10toast不可用则显示GUI通知"""
    try:
        import win10toast
        notifier = win10toast.ToastNotifier()
        notifier.show_toast(title, f"已保存到 {filepath}", duration=NOTIFICATION_DURATION // 1000)
    except ImportError:
        # 如果没有win10toast，则在GUI中显示通知
        if 'app' in globals():
            app.show_notification(message)


def capture_fixed_region():
    """捕获指定屏幕区域并保存为文件"""
    try:
        # 自动应用当前界面设置
        if 'app' in globals():
            app.update_settings()

        # 捕获指定区域
        screenshot = ImageGrab.grab(bbox=REGION)
        filepath = save_screenshot(screenshot, "screenshot")
        show_system_notification("截图成功", f"截图已保存至: {filepath}", filepath)
        screenshot.close()  # 释放资源
    except Exception as e:
        print(f"截图失败: {e}")


def capture_full_screen():
    """捕获全屏并保存为文件"""
    try:
        # 自动应用当前界面设置（主要是保存路径）
        if 'app' in globals():
            app.update_settings()

        # 捕获全屏
        screenshot = ImageGrab.grab()
        filepath = save_screenshot(screenshot, "fullscreen")
        show_system_notification("全屏截图成功", f"全屏截图已保存至: {filepath}", filepath)
        screenshot.close()  # 释放资源
    except Exception as e:
        print(f"全屏截图失败: {e}")


class ScreenshotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("多功能屏幕工具")
        self.root.geometry("950x850")
        self.root.configure(bg=BACKGROUND_COLOR)

        # 创建界面元素
        self.create_widgets()

        # 注册全局快捷键
        keyboard.add_hotkey(HOTKEY, capture_fixed_region)

        # 注册新的复制功能快捷键
        self.register_copy_hotkeys()

        # 状态变量
        self.notification_id = None

        # 开始更新鼠标信息
        self.update_mouse_info()

        # 添加截图预览窗口引用
        self.preview_window = None
        # 添加快捷键说明窗口引用
        self.shortcut_window = None

    def register_copy_hotkeys(self):
        """注册所有复制功能的快捷键"""
        try:
            keyboard.add_hotkey(HOTKEY_COPY_POSITION, self.copy_position)
            keyboard.add_hotkey(HOTKEY_COPY_COLOR, self.copy_rgb)
            keyboard.add_hotkey(HOTKEY_COPY_ALL, self.copy_all)
            keyboard.add_hotkey(HOTKEY_COPY_X, self.copy_x)
            keyboard.add_hotkey(HOTKEY_COPY_Y, self.copy_y)
            keyboard.add_hotkey(HOTKEY_COPY_R, self.copy_r)
            keyboard.add_hotkey(HOTKEY_COPY_G, self.copy_g)
            keyboard.add_hotkey(HOTKEY_COPY_B, self.copy_b)
        except Exception as e:
            print(f"注册快捷键失败: {e}")

    def create_widgets(self):
        # 标题区域
        title_frame = tk.Frame(self.root, bg=BACKGROUND_COLOR)
        title_frame.pack(pady=(10, 5), fill="x", padx=20)

        title_label = tk.Label(title_frame, text="多功能屏幕工具",
                               font=("微软雅黑", 22, "bold"), fg=SECONDARY_COLOR, bg=BACKGROUND_COLOR)
        title_label.pack()

        description_label = tk.Label(title_frame, text="快速区域截图 | 实时坐标RGB显示 | 多功能快捷键",
                                     font=("微软雅黑", 12), fg=LIGHT_TEXT, bg=BACKGROUND_COLOR)
        description_label.pack(pady=(5, 0))



        # 快捷键信息框架
        hotkey_frame = tk.Frame(self.root, bg=BACKGROUND_COLOR)
        hotkey_frame.pack(pady=10)

        # 添加提示信息，居中显示
        hint_frame = tk.Frame(hotkey_frame, bg=BACKGROUND_COLOR)
        hint_frame.pack(side=tk.TOP, fill="x", pady=(0, 5))
        hint_label = tk.Label(hint_frame, text="💡 所有窗口均可手动调整大小",
                              font=("微软雅黑", 10), fg=LIGHT_TEXT, bg=BACKGROUND_COLOR)
        hint_label.pack(expand=True)

        tk.Label(hotkey_frame, text="截图快捷键:", font=("微软雅黑", 12),
                 fg=TEXT_COLOR, bg=BACKGROUND_COLOR).pack(side=tk.LEFT)
        tk.Label(hotkey_frame, text=HOTKEY, font=("Consolas", 13, "bold"),
                 fg=ACCENT_COLOR, bg=BACKGROUND_COLOR).pack(side=tk.LEFT, padx=(5, 0))
        tk.Label(hotkey_frame, text="（设置自动应用，无需手动点击“保存配置”！）", font=("微软雅黑", 10),
                 fg=LIGHT_TEXT, bg=BACKGROUND_COLOR).pack(side=tk.LEFT, padx=(10, 0))





        # 主要功能区域容器
        main_container = tk.Frame(self.root, bg=BACKGROUND_COLOR)
        main_container.pack(pady=15, padx=20, fill="both", expand=True)

        # 鼠标信息框架 - 左侧
        mouse_frame = tk.LabelFrame(main_container, text="鼠标信息面板", padx=15, pady=15,
                                    font=("微软雅黑", 12, "bold"), fg=PRIMARY_COLOR, bg=BACKGROUND_COLOR)
        mouse_frame.pack(side=tk.LEFT, fill="y", padx=(0, 10))

        # 鼠标坐标
        coord_row = tk.Frame(mouse_frame, bg=LIGHT_BACKGROUND)
        coord_row.pack(fill="x", pady=8)
        tk.Label(coord_row, text="坐标(X,Y):", font=("微软雅黑", 11), width=10,
                 fg=TEXT_COLOR, bg=LIGHT_BACKGROUND).pack(side=tk.LEFT)
        self.coord_label = tk.Label(coord_row, text="0, 0", font=("Consolas", 11, "bold"),
                                    fg=PRIMARY_COLOR, bg=LIGHT_BACKGROUND)
        self.coord_label.pack(side=tk.LEFT, padx=(5, 0))

        # RGB值
        rgb_row = tk.Frame(mouse_frame, bg=LIGHT_BACKGROUND)
        rgb_row.pack(fill="x", pady=8)
        tk.Label(rgb_row, text="颜色RGB:", font=("微软雅黑", 11), width=10,
                 fg=TEXT_COLOR, bg=LIGHT_BACKGROUND).pack(side=tk.LEFT)
        self.rgb_label = tk.Label(rgb_row, text="0, 0, 0", font=("Consolas", 11, "bold"),
                                  fg=ACCENT_COLOR, bg=LIGHT_BACKGROUND)
        self.rgb_label.pack(side=tk.LEFT, padx=(5, 0))

        # 复制按钮框架 - 垂直排列
        copy_frame = tk.Frame(mouse_frame, bg=LIGHT_BACKGROUND)
        copy_frame.pack(fill="x", pady=12)

        # 主要复制按钮
        copy_main_frame = tk.Frame(copy_frame, bg=LIGHT_BACKGROUND)
        copy_main_frame.pack(fill="x", pady=(0, 8))
        tk.Button(copy_main_frame, text="复制坐标", command=self.copy_position,
                  bg=BUTTON_COLORS["copy"], fg="white", font=("微软雅黑", 10),
                  height=1, relief="flat").pack(side=tk.LEFT, padx=2, expand=True, fill="x")
        tk.Button(copy_main_frame, text="复制颜色", command=self.copy_rgb,
                  bg=BUTTON_COLORS["rgb"], fg="white", font=("微软雅黑", 10),
                  height=1, relief="flat").pack(side=tk.LEFT, padx=2, expand=True, fill="x")
        tk.Button(copy_main_frame, text="全部复制", command=self.copy_all,
                  bg=BUTTON_COLORS["all"], fg="white", font=("微软雅黑", 10),
                  height=1, relief="flat").pack(side=tk.LEFT, padx=2, expand=True, fill="x")

        # 单独值复制按钮 - 水平排列
        single_copy_frame = tk.Frame(copy_frame, bg=LIGHT_BACKGROUND)
        single_copy_frame.pack(fill="x")
        tk.Label(single_copy_frame, text="单值复制:", font=("微软雅黑", 10),
                 fg=TEXT_COLOR, bg=LIGHT_BACKGROUND).pack(side=tk.LEFT)
        tk.Button(single_copy_frame, text="X", command=self.copy_x, width=3,
                  font=("Consolas", 9), bg=BUTTON_COLORS["single"], fg="white").pack(side=tk.LEFT, padx=2)
        tk.Button(single_copy_frame, text="Y", command=self.copy_y, width=3,
                  font=("Consolas", 9), bg=BUTTON_COLORS["single"], fg="white").pack(side=tk.LEFT, padx=2)
        tk.Button(single_copy_frame, text="R", command=self.copy_r, width=3,
                  font=("Consolas", 9), bg=BUTTON_COLORS["single"], fg="white").pack(side=tk.LEFT, padx=2)
        tk.Button(single_copy_frame, text="G", command=self.copy_g, width=3,
                  font=("Consolas", 9), bg=BUTTON_COLORS["single"], fg="white").pack(side=tk.LEFT, padx=2)
        tk.Button(single_copy_frame, text="B", command=self.copy_b, width=3,
                  font=("Consolas", 9), bg=BUTTON_COLORS["single"], fg="white").pack(side=tk.LEFT, padx=2)

        # 添加快捷键提示标签
        shortcut_label_frame = tk.Frame(mouse_frame, bg=LIGHT_BACKGROUND)
        shortcut_label_frame.pack(fill="x", pady=8)
        shortcut_label = tk.Label(shortcut_label_frame, text="💡 所有复制功能支持快捷键操作，详情请点击“快捷键一览”",
                                  font=("微软雅黑", 9), fg=LIGHT_TEXT, bg=LIGHT_BACKGROUND)
        shortcut_label.pack()

        # 区域设置框架 - 右侧
        settings_frame = tk.Frame(main_container, bg=BACKGROUND_COLOR)
        settings_frame.pack(side=tk.RIGHT, fill="both", expand=True)

        # 区域设置框架
        region_frame = tk.LabelFrame(settings_frame, text="截图区域设置", padx=15, pady=15,
                                     font=("微软雅黑", 12, "bold"), fg=PRIMARY_COLOR, bg=BACKGROUND_COLOR)
        region_frame.pack(fill="both", expand=True, pady=(0, 10))

        # 区域输入区域
        input_frame = tk.Frame(region_frame, bg=LIGHT_BACKGROUND)
        input_frame.pack(fill="x", pady=8)

        # 左边上边
        row1 = tk.Frame(input_frame, bg=LIGHT_BACKGROUND)
        row1.pack(fill="x", pady=6)
        tk.Label(row1, text="左边界:", width=10, font=("微软雅黑", 10),
                 fg=TEXT_COLOR, bg=LIGHT_BACKGROUND).pack(side=tk.LEFT)
        self.left_entry = tk.Entry(row1, width=12, font=("Consolas", 10),
                                   relief="solid", borderwidth=1)
        self.left_entry.insert(0, str(LEFT))
        self.left_entry.pack(side=tk.LEFT, padx=5, fill="x", expand=True)

        tk.Label(row1, text="上边界:", width=10, font=("微软雅黑", 10),
                 fg=TEXT_COLOR, bg=LIGHT_BACKGROUND).pack(side=tk.LEFT, padx=(10, 0))
        self.up_entry = tk.Entry(row1, width=12, font=("Consolas", 10),
                                 relief="solid", borderwidth=1)
        self.up_entry.insert(0, str(UP))
        self.up_entry.pack(side=tk.LEFT, padx=5, fill="x", expand=True)

        # 右边下边
        row2 = tk.Frame(input_frame, bg=LIGHT_BACKGROUND)
        row2.pack(fill="x", pady=6)
        tk.Label(row2, text="右边界:", width=10, font=("微软雅黑", 10),
                 fg=TEXT_COLOR, bg=LIGHT_BACKGROUND).pack(side=tk.LEFT)
        self.right_entry = tk.Entry(row2, width=12, font=("Consolas", 10),
                                    relief="solid", borderwidth=1)
        self.right_entry.insert(0, str(RIGHT))
        self.right_entry.pack(side=tk.LEFT, padx=5, fill="x", expand=True)

        tk.Label(row2, text="下边界:", width=10, font=("微软雅黑", 10),
                 fg=TEXT_COLOR, bg=LIGHT_BACKGROUND).pack(side=tk.LEFT, padx=(10, 0))
        self.down_entry = tk.Entry(row2, width=12, font=("Consolas", 10),
                                   relief="solid", borderwidth=1)
        self.down_entry.insert(0, str(DOWN))
        self.down_entry.pack(side=tk.LEFT, padx=5, fill="x", expand=True)

        # 预览区域按钮
        preview_button_frame = tk.Frame(region_frame, bg=LIGHT_BACKGROUND)
        preview_button_frame.pack(fill="x", pady=10)
        tk.Button(preview_button_frame, text="预览截图区域", command=self.preview_current_region,
                  bg=BUTTON_COLORS["preview"], fg="white", font=("微软雅黑", 10),
                  relief="flat").pack(side=tk.LEFT, padx=2, expand=True, fill="x")
        tk.Button(preview_button_frame, text="可视化选择区域", command=self.open_drag_selection,
                  bg=BUTTON_COLORS["drag"], fg="white", font=("微软雅黑", 10),
                  relief="flat").pack(side=tk.LEFT, padx=2, expand=True, fill="x")

        # 目录设置
        dir_frame = tk.Frame(settings_frame, bg=BACKGROUND_COLOR)
        dir_frame.pack(fill="x", pady=(0, 10))

        tk.Label(dir_frame, text="截图保存目录:", font=("微软雅黑", 11),
                 fg=TEXT_COLOR, bg=BACKGROUND_COLOR).pack(side=tk.LEFT)
        self.dir_entry = tk.Entry(dir_frame, width=25, font=("微软雅黑", 10),
                                  relief="solid", borderwidth=1)
        self.dir_entry.insert(0, SCREENSHOT_DIR)
        self.dir_entry.pack(side=tk.LEFT, padx=10, fill="x", expand=True)

        browse_btn = tk.Button(dir_frame, text="浏览目录", command=self.browse_directory,
                               bg=BUTTON_COLORS["browse"], fg="white", font=("微软雅黑", 9),
                               relief="flat", width=8)
        browse_btn.pack(side=tk.LEFT, padx=5)

        # 操作按钮框架 - 底部居中
        button_frame = tk.Frame(self.root, bg=BACKGROUND_COLOR)
        button_frame.pack(pady=15, padx=20, fill="x")

        # 创建按钮网格布局（移除了"应用设置"和"保存配置"按钮）
        buttons = [
            ("区域截图", self.one_click_capture, BUTTON_COLORS["capture"]),
            ("全屏截图", self.fullscreen_capture, BUTTON_COLORS["fullscreen"]),
            ("快捷键一览", self.show_shortcuts, BUTTON_COLORS["shortcut"]),  # 新增快捷键一览按钮
            ("保存配置", self.save_settings, BUTTON_COLORS["save"]),  # 保留手动保存配置选项
            ("退出程序", self.root.quit, BUTTON_COLORS["exit"])
        ]

        for i, (text, command, color) in enumerate(buttons):
            tk.Button(button_frame, text=text, command=command,
                      bg=color, fg="white", font=("微软雅黑", 11, "bold"),
                      relief="flat", padx=15, pady=8).grid(
                row=0, column=i, padx=5, sticky="ew", ipady=2)

        # 配置列权重，使按钮平均分布
        for i in range(len(buttons)):
            button_frame.grid_columnconfigure(i, weight=1)

        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪 - 设置自动应用，无需手动保存配置")
        status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN,
                              anchor=tk.W, font=("微软雅黑", 10), fg=LIGHT_TEXT, bg=LIGHT_BACKGROUND)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

    def update_mouse_info(self):
        """更新鼠标坐标和RGB值"""
        try:
            # 获取鼠标坐标
            x, y = pyautogui.position()
            self.coord_label.config(text=f"{x}, {y}")

            # 获取鼠标位置的RGB值，只获取一次截图
            screenshot = pyautogui.screenshot()
            r, g, b = screenshot.getpixel((x, y))
            self.rgb_label.config(text=f"{r}, {g}, {b}")
            screenshot.close()  # 释放资源
        except Exception as e:
            pass  # 忽略可能的异常

        # 每100毫秒更新一次
        self.root.after(UPDATE_INTERVAL, self.update_mouse_info)

    def copy_position(self):
        """复制鼠标坐标到剪贴板"""
        try:
            x, y = pyautogui.position()
            pos_text = f"{x}, {y}"
            pyperclip.copy(pos_text)
            self.status_var.set("坐标已复制到剪贴板")
            self.root.after(NOTIFICATION_DURATION, lambda: self.status_var.set("就绪 - 设置自动应用，无需手动保存配置"))
        except Exception as e:
            self.status_var.set(f"复制坐标失败: {str(e)}")
            self.root.after(NOTIFICATION_DURATION, lambda: self.status_var.set("就绪 - 设置自动应用，无需手动保存配置"))

    def copy_rgb(self):
        """复制RGB值到剪贴板"""
        try:
            x, y = pyautogui.position()
            # 获取鼠标位置的RGB值
            screenshot = pyautogui.screenshot()
            r, g, b = screenshot.getpixel((x, y))
            screenshot.close()  # 释放资源
            rgb_text = f"{r}, {g}, {b}"
            pyperclip.copy(rgb_text)
            self.status_var.set("RGB值已复制到剪贴板")
        except Exception as e:
            self.status_var.set(f"复制RGB值失败: {str(e)}")
        finally:
            self.root.after(NOTIFICATION_DURATION, lambda: self.status_var.set("就绪 - 设置自动应用，无需手动保存配置"))

    def copy_all(self):
        """复制所有信息到剪贴板"""
        try:
            x, y = pyautogui.position()
            # 获取鼠标位置的RGB值
            screenshot = pyautogui.screenshot()
            r, g, b = screenshot.getpixel((x, y))
            screenshot.close()  # 释放资源
            all_text = f"坐标: {x}, {y}\nRGB: {r}, {g}, {b}"
            pyperclip.copy(all_text)
            self.status_var.set("全部信息已复制到剪贴板")
        except Exception as e:
            self.status_var.set(f"复制全部信息失败: {str(e)}")
        finally:
            self.root.after(NOTIFICATION_DURATION, lambda: self.status_var.set("就绪 - 设置自动应用，无需手动保存配置"))

    def copy_x(self):
        """复制X坐标值到剪贴板"""
        try:
            x, y = pyautogui.position()
            pyperclip.copy(str(x))
            self.status_var.set("X坐标已复制到剪贴板")
        except Exception as e:
            self.status_var.set(f"复制X坐标失败: {str(e)}")
        finally:
            self.root.after(NOTIFICATION_DURATION, lambda: self.status_var.set("就绪 - 设置自动应用，无需手动保存配置"))

    def copy_y(self):
        """复制Y坐标值到剪贴板"""
        try:
            x, y = pyautogui.position()
            pyperclip.copy(str(y))
            self.status_var.set("Y坐标已复制到剪贴板")
        except Exception as e:
            self.status_var.set(f"复制Y坐标失败: {str(e)}")
        finally:
            self.root.after(NOTIFICATION_DURATION, lambda: self.status_var.set("就绪 - 设置自动应用，无需手动保存配置"))

    def copy_r(self):
        """复制R颜色值到剪贴板"""
        try:
            x, y = pyautogui.position()
            # 获取鼠标位置的RGB值
            screenshot = pyautogui.screenshot()
            r, g, b = screenshot.getpixel((x, y))
            screenshot.close()  # 释放资源
            pyperclip.copy(str(r))
            self.status_var.set("R值已复制到剪贴板")
        except Exception as e:
            self.status_var.set("无法获取RGB值")
        finally:
            self.root.after(NOTIFICATION_DURATION, lambda: self.status_var.set("就绪 - 设置自动应用，无需手动保存配置"))

    def copy_g(self):
        """复制G颜色值到剪贴板"""
        try:
            x, y = pyautogui.position()
            # 获取鼠标位置的RGB值
            screenshot = pyautogui.screenshot()
            r, g, b = screenshot.getpixel((x, y))
            screenshot.close()  # 释放资源
            pyperclip.copy(str(g))
            self.status_var.set("G值已复制到剪贴板")
        except Exception as e:
            self.status_var.set("无法获取RGB值")
        finally:
            self.root.after(NOTIFICATION_DURATION, lambda: self.status_var.set("就绪 - 设置自动应用，无需手动保存配置"))

    def copy_b(self):
        """复制B颜色值到剪贴板"""
        try:
            x, y = pyautogui.position()
            # 获取鼠标位置的RGB值
            screenshot = pyautogui.screenshot()
            r, g, b = screenshot.getpixel((x, y))
            screenshot.close()  # 释放资源
            pyperclip.copy(str(b))
            self.status_var.set("B值已复制到剪贴板")
        except Exception as e:
            self.status_var.set("无法获取RGB值")
        finally:
            self.root.after(NOTIFICATION_DURATION, lambda: self.status_var.set("就绪 - 设置自动应用，无需手动保存配置"))

    def browse_directory(self):
        """浏览并选择保存目录"""
        directory = filedialog.askdirectory()
        if directory:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, directory)

    def one_click_capture(self):
        """一键截图功能，自动应用当前设置"""
        try:
            # 自动应用当前设置
            self.update_settings()
            capture_fixed_region()
            self.status_var.set("截图已完成（设置已自动应用）")
        except Exception as e:
            self.status_var.set(f"截图失败: {str(e)}")
        finally:
            self.root.after(NOTIFICATION_DURATION, lambda: self.status_var.set("就绪 - 设置自动应用，无需手动保存配置"))

    def fullscreen_capture(self):
        """全屏截图，自动应用当前设置"""
        try:
            # 自动应用当前设置（主要是保存路径）
            self.update_settings()
            capture_full_screen()
            self.status_var.set("全屏截图已完成（设置已自动应用）")
        except Exception as e:
            self.status_var.set(f"全屏截图失败: {str(e)}")
        finally:
            self.root.after(NOTIFICATION_DURATION, lambda: self.status_var.set("就绪 - 设置自动应用，无需手动保存配置"))

    def update_settings(self):
        """更新全局设置（内化到截图操作中）"""
        global LEFT, UP, RIGHT, DOWN, REGION, SCREENSHOT_DIR
        try:
            LEFT = int(self.left_entry.get())
            UP = int(self.up_entry.get())
            RIGHT = int(self.right_entry.get())
            DOWN = int(self.down_entry.get())
            SCREENSHOT_DIR = self.dir_entry.get()

            REGION = (LEFT, UP, RIGHT, DOWN)
            return True
        except ValueError as e:
            self.status_var.set(f"设置更新失败: 请输入有效的数字!")
            return False

    def save_settings(self):
        """手动保存配置（可选功能）"""
        if self.update_settings():
            messagebox.showinfo("成功", "设置已保存!")

    def show_notification(self, message):
        self.status_var.set(message)
        self.root.after(NOTIFICATION_DURATION, lambda: self.status_var.set("就绪 - 设置自动应用，无需手动保存配置"))

    def show_shortcuts(self):
        """显示快捷键一览窗口"""
        if self.shortcut_window:
            self.shortcut_window.destroy()

        self.shortcut_window = tk.Toplevel(self.root)
        self.shortcut_window.title("快捷键一览")
        self.shortcut_window.geometry("500x800")
        self.shortcut_window.configure(bg=BACKGROUND_COLOR)
        self.shortcut_window.resizable(True, True)

        # 设置窗口图标和置顶
        try:
            self.shortcut_window.attributes('-topmost', True)
        except:
            pass

        # 标题
        title_label = tk.Label(self.shortcut_window, text="📋 快捷键一览表",
                               font=("微软雅黑", 16, "bold"), fg=SECONDARY_COLOR, bg=BACKGROUND_COLOR)
        title_label.pack(pady=15)

        # 创建快捷键表格框架
        table_frame = tk.Frame(self.shortcut_window, bg=BACKGROUND_COLOR)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # 快捷键数据
        shortcuts = [
            ("功能描述", "快捷键", "备注"),
            ("─" * 30, "─" * 20, "─" * 30),  # 分隔线
            ("区域截图", HOTKEY, "主截图功能"),
            ("全屏截图", "GUI按钮", "通过界面按钮操作"),
            ("复制坐标", HOTKEY_COPY_POSITION, "复制当前鼠标坐标"),
            ("复制颜色", HOTKEY_COPY_COLOR, "复制当前鼠标位置RGB值"),
            ("全部复制", HOTKEY_COPY_ALL, "同时复制坐标和颜色"),
            ("复制X坐标", HOTKEY_COPY_X, "仅复制X坐标值"),
            ("复制Y坐标", HOTKEY_COPY_Y, "仅复制Y坐标值"),
            ("复制R值", HOTKEY_COPY_R, "仅复制RGB中的R值"),
            ("复制G值", HOTKEY_COPY_G, "仅复制RGB中的G值"),
            ("复制B值", HOTKEY_COPY_B, "仅复制RGB中的B值"),
            ("退出程序", "ESC", "完全退出应用程序")
        ]

        # 创建表格
        for i, (description, shortcut, remark) in enumerate(shortcuts):
            # 设置行背景色
            if i == 0:  # 表头
                bg_color = PRIMARY_COLOR
                fg_color = "white"
                font_weight = "bold"
            elif i == 1:  # 分隔线
                bg_color = LIGHT_BACKGROUND
                fg_color = LIGHT_TEXT
                font_weight = "normal"
            else:
                bg_color = LIGHT_BACKGROUND if i % 2 == 0 else BACKGROUND_COLOR
                fg_color = TEXT_COLOR
                font_weight = "normal"

            row_frame = tk.Frame(table_frame, bg=bg_color)
            row_frame.pack(fill="x", pady=1)

            # 功能描述列
            desc_label = tk.Label(row_frame, text=description, font=("微软雅黑", 10, font_weight),
                                  fg=fg_color, bg=bg_color, anchor="w", width=20)
            desc_label.pack(side=tk.LEFT, padx=5, pady=3)

            # 快捷键列
            shortcut_label = tk.Label(row_frame, text=shortcut, font=("Consolas", 10, "bold"),
                                      fg=ACCENT_COLOR if i > 1 else fg_color, bg=bg_color,
                                      anchor="w", width=20)
            shortcut_label.pack(side=tk.LEFT, padx=5, pady=3)

            # 备注列
            remark_label = tk.Label(row_frame, text=remark, font=("微软雅黑", 9, font_weight),
                                    fg=fg_color, bg=bg_color, anchor="w", width=25)
            remark_label.pack(side=tk.LEFT, padx=5, pady=3, fill="x", expand=True)

        # 使用说明
        tip_frame = tk.Frame(self.shortcut_window, bg=LIGHT_BACKGROUND)
        tip_frame.pack(fill="x", padx=20, pady=15)

        tips = [
            "💡 提示：",
            "• 所有快捷键均为全局热键，在任何界面下都有效",
            "• 快捷键操作后会有状态提示",
            "• 鼠标悬停界面按钮可查看功能说明"
        ]

        for tip in tips:
            tip_label = tk.Label(tip_frame, text=tip, font=("微软雅黑", 9),
                                 fg=TEXT_COLOR, bg=LIGHT_BACKGROUND, anchor="w")
            tip_label.pack(anchor="w", pady=1)

        # 关闭按钮
        close_btn = tk.Button(self.shortcut_window, text="关闭", command=self.shortcut_window.destroy,
                              bg=BUTTON_COLORS["exit"], fg="white", font=("微软雅黑", 10),
                              relief="flat", width=15, pady=5)
        close_btn.pack(pady=10)

    def preview_current_region(self):
        """预览当前设置的截图区域"""
        try:
            # 先应用当前设置
            if not self.update_settings():
                return

            # 获取当前区域设置
            left = int(self.left_entry.get())
            up = int(self.up_entry.get())
            right = int(self.right_entry.get())
            down = int(self.down_entry.get())

            # 捕获当前区域截图
            region = (left, up, right, down)
            screenshot = ImageGrab.grab(bbox=region)

            # 创建预览窗口
            if self.preview_window:
                self.preview_window.destroy()

            self.preview_window = tk.Toplevel(self.root)
            self.preview_window.title("区域预览")
            self.preview_window.geometry(f"400x300")
            self.preview_window.protocol("WM_DELETE_WINDOW", self.close_preview_window)

            # 计算缩放比例以适应窗口
            img_width, img_height = screenshot.size
            max_width, max_height = 380, 260
            scale = min(max_width / img_width, max_height / img_height)
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)

            # 调整图像大小
            resized_img = screenshot.resize((new_width, new_height))

            # 将图片转换为tkinter可用的格式
            photo = tk.PhotoImage(master=self.preview_window, width=new_width, height=new_height)
            resized_img.save("temp_preview.png")
            photo = tk.PhotoImage(file="temp_preview.png")

            # 显示预览图像
            label = tk.Label(self.preview_window, image=photo)
            label.image = photo  # 保持引用防止被垃圾回收
            label.pack(pady=10)

            # 添加区域信息标签
            region_info = f"区域: ({left}, {up}) 到 ({right}, {down})"
            info_label = tk.Label(self.preview_window, text=region_info)
            info_label.pack()

            screenshot.close()  # 释放资源

        except Exception as e:
            messagebox.showerror("错误", f"预览失败: {str(e)}")

    def close_preview_window(self):
        """关闭预览窗口并删除临时文件"""
        if self.preview_window:
            try:
                import os
                if os.path.exists("temp_preview.png"):
                    os.remove("temp_preview.png")
            except:
                pass
            self.preview_window.destroy()
            self.preview_window = None

    def open_drag_selection(self):
        """打开拖拽选择区域的窗口"""
        # 创建覆盖全屏的透明窗口用于拖拽选择
        self.drag_window = tk.Toplevel(self.root)
        self.drag_window.attributes('-alpha', 0.3)  # 设置透明度
        self.drag_window.attributes('-topmost', True)  # 置顶
        self.drag_window.overrideredirect(True)  # 无边框窗口
        self.drag_window.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0")

        # 绑定鼠标事件
        self.drag_start_x = None
        self.drag_start_y = None
        self.drag_rect = None

        self.drag_window.bind("<ButtonPress-1>", self.on_drag_start)
        self.drag_window.bind("<B1-Motion>", self.on_drag_motion)
        self.drag_window.bind("<ButtonRelease-1>", self.on_drag_release)

    def on_drag_start(self, event):
        """开始拖拽"""
        self.drag_start_x = event.x_root
        self.drag_start_y = event.y_root
        # 创建矩形表示选区
        self.drag_rect = tk.Canvas(
            self.drag_window,
            highlightthickness=0,
            bg='blue',
            cursor='crosshair'
        )
        self.drag_rect.place(x=self.drag_start_x, y=self.drag_start_y, width=1, height=1)

    def on_drag_motion(self, event):
        """拖拽过程中的移动"""
        if self.drag_rect and self.drag_start_x and self.drag_start_y:
            x1, y1 = self.drag_start_x, self.drag_start_y
            x2, y2 = event.x_root, event.y_root
            self.drag_rect.place(
                x=min(x1, x2),
                y=min(y1, y2),
                width=abs(x2 - x1),
                height=abs(y2 - y1)
            )

    def on_drag_release(self, event):
        """结束拖拽并记录区域"""
        if self.drag_rect:
            # 获取最终的矩形坐标
            x1 = self.drag_rect.winfo_x()
            y1 = self.drag_rect.winfo_y()
            x2 = x1 + self.drag_rect.winfo_width()
            y2 = y1 + self.drag_rect.winfo_height()

            # 更新界面上的数值
            self.left_entry.delete(0, tk.END)
            self.left_entry.insert(0, str(x1))
            self.up_entry.delete(0, tk.END)
            self.up_entry.insert(0, str(y1))
            self.right_entry.delete(0, tk.END)
            self.right_entry.insert(0, str(x2))
            self.down_entry.delete(0, tk.END)
            self.down_entry.insert(0, str(y2))

            # 关闭拖拽窗口
            self.drag_window.destroy()

            # 自动更新全局变量
            self.update_settings()


def main():
    print(f"屏幕截图程序已启动! 按下 {HOTKEY} 捕获区域 {REGION}")
    print("按ESC退出程序")

    # 同时支持GUI和快捷键
    root = tk.Tk()
    global app
    app = ScreenshotApp(root)

    # 在新线程中监听键盘事件
    keyboard_thread = threading.Thread(target=lambda: keyboard.wait("esc"), daemon=True)
    keyboard_thread.start()

    # 运行GUI主循环
    root.mainloop()


if __name__ == "__main__":
    main()