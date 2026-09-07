# superPrintscreen_beta

多功能截图与鼠标取色工具：区域/全屏截图、实时显示鼠标坐标与 RGB、一键/热键复制坐标或颜色。
基于 Python/Tkinter/Pillow/PyAutoGUI/keyboard/pyperclip。

## Features
- 固定区域截图：默认 bbox 可在界面设置左/上/右/下，热键 Ctrl+Alt+Q
- 全屏截图按钮
- 实时鼠标坐标 (X,Y) 与像素 RGB 显示（轮询更新）
- 复制热键：
  - Ctrl+Alt+Shift+A 复制坐标
  - Ctrl+Alt+Shift+S 复制 RGB
  - Ctrl+Alt+Shift+D 复制“坐标+RGB”
  - 单值：X/Z? 见下（源码热键映射以实际为准）
    - 源码当前：Z→X，X→Y，C→R，V→G，B→B
  - 界面按钮同样支持单值/全量复制
- 可视化拖拽选区域、区域预览
- 自定义保存目录、时间戳命名、系统通知（win10toast 可选）

## Requirements
- Python 3.8+
- Pillow（ImageGrab/Image）
- pyautogui（坐标、截屏回退）
- keyboard（全局热键）
- pyperclip（剪贴板）
- Tkinter（标准库；Linux 补 python3-tk）
- 可选：win10toast（Windows 系统通知）

## Install
git clone https://github.com/berserkross/superPrintscreen_beta.git
cd superPrintscreen_beta
pip install -r requirements.txt
# 最低：pip install Pillow pyautogui keyboard pyperclip

## Usage
python superPrintscreen_beta.py
1. 设置截图区域左右上下，或“可视化选择区域”框选
2. 设保存目录；“区域截图”用 Ctrl+Alt+Q，或点按钮
3. 移动鼠标，面板实时显示坐标/RGB；用热键或按钮复制
4. “快捷键一览”查看全部绑定

## Platform notes
- Windows：ImageGrab 通常可用；全局热键以普通用户运行。
- macOS：截图可能走 Pillow/ImageGrab 或系统后端；若用 pyautogui 截图，
  需在“隐私与安全性→屏幕录制/辅助功能”授权终端/IDE。[6,9](@ref)
  Retina 下逻辑坐标与物理像素可能不同，取色坐标需注意缩放。
- Linux：ImageGrab 对 X11 支持有限，Wayland 常需 xdg-desktop-portal/授权；
  可用 pyautogui.screenshot 或 mss 作替代后端。部分环境需 scrot、python3-xlib、python3-tk。[1,3,6](@ref)
- 多显示器：PyAutoGUI/ImageGrab 默认主屏行为不一致，绝对区域要按主屏分辨率调。[2](@ref)

## Known limitations (beta)
- 坐标/RGB 轮询约 100ms，高刷新场景有轻微延迟
- 全局热键依赖 keyboard，部分系统/IDE 需 root 或辅助权限
- 临时预览会写 temp_preview.png，关闭预览自动清理
- 默认 REGION 硬编码示例值，使用前按自己分辨率改界面或代码常量

## Possible research/automation use
UI 标注取色、测试截图回归、数据集样本框选、桌面工作流自动化原型。
