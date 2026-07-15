"""
YVR助手 - 主题和样式配置
"""

# 颜色方案 - 深色科技风
COLORS = {
    "bg_dark": "#0F0F14",
    "bg_sidebar": "#15151E",
    "bg_card": "#1C1C28",
    "bg_card_hover": "#242438",
    "bg_input": "#1A1A28",
    "bg_header": "#12121A",

    "accent": "#6C5CE7",
    "accent_light": "#A29BFE",
    "accent_dark": "#5541C8",

    "success": "#00D68F",
    "warning": "#FFAA00",
    "danger": "#FF4757",
    "info": "#45AAF2",

    "text_primary": "#EAEAF0",
    "text_secondary": "#9A9AB0",
    "text_muted": "#6B6B80",

    "border": "#2A2A3C",
    "border_light": "#383850",

    "gradient_start": "#6C5CE7",
    "gradient_end": "#45AAF2",
}

# 字体配置
FONTS = {
    "title": ("Microsoft YaHei UI", 24, "bold"),
    "subtitle": ("Microsoft YaHei UI", 16, "bold"),
    "heading": ("Microsoft YaHei UI", 13, "bold"),
    "body": ("Microsoft YaHei UI", 12),
    "body_bold": ("Microsoft YaHei UI", 12, "bold"),
    "small": ("Microsoft YaHei UI", 10),
    "mono": ("Consolas", 11),
    "button": ("Microsoft YaHei UI", 13, "bold"),
    "sidebar": ("Microsoft YaHei UI", 12, "bold"),
}

# 侧边栏按钮图标 (Unicode 符号)
NAV_ICONS = {
    "设备信息": "\ue770",     # 电脑/设备图标
    "安装游戏": "\ue7fc",     # 下载/安装图标
    "文件管理": "\ue8b7",     # 文件夹图标
    "Root": "\ue7a3",        # 盾牌/管理员图标
    "VR投屏": "\ue7c7",        # 投屏/显示器图标
    "ADB命令": "\ue943",      # 终端/命令行图标
}