"""
YVR助手 - 桌面端全局样式表
深色现代主题，科技感十足
"""

# 颜色常量
PRIMARY = "#6C5CE7"
PRIMARY_HOVER = "#7C6FF7"
PRIMARY_DARK = "#5A4BD1"
ACCENT = "#00D2FF"
ACCENT_DARK = "#00B8E6"
SUCCESS = "#00E676"
WARNING = "#FFD740"
DANGER = "#FF5252"
BG_DARK = "#0F0F1A"
BG_SIDEBAR = "#13132A"
BG_CARD = "#1A1A35"
BG_INPUT = "#222240"
BG_HOVER = "#252545"
TEXT_PRIMARY = "#EAEAEF"
TEXT_SECONDARY = "#8888A0"
TEXT_MUTED = "#5A5A7A"
BORDER = "#2A2A4A"


def get_stylesheet():
    """获取全局 QSS 样式表"""
    return f"""
    /* ========== 全局 ========== */
    QWidget {{
        background-color: {BG_DARK};
        color: {TEXT_PRIMARY};
        font-family: "Microsoft YaHei", "PingFang SC", "Segoe UI", sans-serif;
        font-size: 13px;
    }}

    /* ========== 滚动条 ========== */
    QScrollBar:vertical {{
        background: {BG_DARK};
        width: 8px;
        border-radius: 4px;
    }}
    QScrollBar::handle:vertical {{
        background: {BORDER};
        border-radius: 4px;
        min-height: 30px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {PRIMARY};
    }}
    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {{
        height: 0px;
    }}

    QScrollBar:horizontal {{
        background: {BG_DARK};
        height: 8px;
        border-radius: 4px;
    }}
    QScrollBar::handle:horizontal {{
        background: {BORDER};
        border-radius: 4px;
        min-width: 30px;
    }}
    QScrollBar::handle:horizontal:hover {{
        background: {PRIMARY};
    }}
    QScrollBar::add-line:horizontal,
    QScrollBar::sub-line:horizontal {{
        width: 0px;
    }}

    /* ========== 按钮 ========== */
    QPushButton {{
        background-color: {PRIMARY};
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-size: 13px;
        font-weight: 600;
        min-height: 20px;
    }}
    QPushButton:hover {{
        background-color: {PRIMARY_HOVER};
    }}
    QPushButton:pressed {{
        background-color: {PRIMARY_DARK};
    }}
    QPushButton:disabled {{
        background-color: {BORDER};
        color: {TEXT_MUTED};
    }}

    QPushButton#btnDanger {{
        background-color: {DANGER};
    }}
    QPushButton#btnDanger:hover {{
        background-color: #FF6E6E;
    }}

    QPushButton#btnSuccess {{
        background-color: {SUCCESS};
        color: #1a1a2e;
    }}
    QPushButton#btnSuccess:hover {{
        background-color: #69F0AE;
    }}

    QPushButton#btnOutline {{
        background-color: transparent;
        border: 1.5px solid {PRIMARY};
        color: {PRIMARY};
    }}
    QPushButton#btnOutline:hover {{
        background-color: rgba(108, 92, 231, 0.1);
    }}

    /* ========== 输入框 ========== */
    QLineEdit, QTextEdit, QPlainTextEdit {{
        background-color: {BG_INPUT};
        border: 1.5px solid {BORDER};
        border-radius: 8px;
        padding: 10px 14px;
        color: {TEXT_PRIMARY};
        font-size: 13px;
        selection-background-color: {PRIMARY};
    }}
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
        border-color: {PRIMARY};
    }}
    QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {{
        background-color: {BG_CARD};
        color: {TEXT_MUTED};
    }}

    /* ========== 标签 ========== */
    QLabel {{
        color: {TEXT_PRIMARY};
        background: transparent;
        border: none;
    }}

    /* ========== 分组框 ========== */
    QGroupBox {{
        background-color: {BG_CARD};
        border: 1px solid {BORDER};
        border-radius: 12px;
        margin-top: 16px;
        padding: 20px 16px 16px 16px;
        font-weight: bold;
        font-size: 14px;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 16px;
        padding: 0 8px;
        color: {PRIMARY};
    }}

    /* ========== 列表 ========== */
    QListWidget {{
        background-color: {BG_CARD};
        border: 1px solid {BORDER};
        border-radius: 10px;
        padding: 8px;
        outline: none;
    }}
    QListWidget::item {{
        padding: 10px 12px;
        border-radius: 6px;
        margin: 2px 0;
    }}
    QListWidget::item:hover {{
        background-color: {BG_HOVER};
    }}
    QListWidget::item:selected {{
        background-color: rgba(108, 92, 231, 0.2);
        color: {PRIMARY};
    }}

    /* ========== 表格 ========== */
    QTableWidget {{
        background-color: {BG_CARD};
        border: 1px solid {BORDER};
        border-radius: 10px;
        gridline-color: {BORDER};
        selection-background-color: rgba(108, 92, 231, 0.2);
    }}
    QTableWidget::item {{
        padding: 8px 12px;
    }}
    QHeaderView::section {{
        background-color: {BG_SIDEBAR};
        color: {TEXT_SECONDARY};
        padding: 10px 12px;
        border: none;
        border-bottom: 1px solid {BORDER};
        font-weight: bold;
        font-size: 12px;
    }}

    /* ========== 进度条 ========== */
    QProgressBar {{
        background-color: {BG_INPUT};
        border: none;
        border-radius: 6px;
        height: 8px;
        text-align: center;
        font-size: 11px;
        color: {TEXT_SECONDARY};
    }}
    QProgressBar::chunk {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {PRIMARY}, stop:1 {ACCENT});
        border-radius: 6px;
    }}

    /* ========== 复选框 ========== */
    QCheckBox {{
        spacing: 10px;
        color: {TEXT_PRIMARY};
    }}
    QCheckBox::indicator {{
        width: 20px;
        height: 20px;
        border: 2px solid {BORDER};
        border-radius: 4px;
        background: {BG_INPUT};
    }}
    QCheckBox::indicator:checked {{
        background: {PRIMARY};
        border-color: {PRIMARY};
    }}

    /* ========== 下拉框 ========== */
    QComboBox {{
        background-color: {BG_INPUT};
        border: 1.5px solid {BORDER};
        border-radius: 8px;
        padding: 10px 14px;
        color: {TEXT_PRIMARY};
        min-width: 120px;
    }}
    QComboBox:hover {{
        border-color: {PRIMARY};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 30px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {BG_CARD};
        border: 1px solid {BORDER};
        border-radius: 8px;
        selection-background-color: rgba(108, 92, 231, 0.2);
        padding: 4px;
    }}

    /* ========== 分割线 ========== */
    QFrame#separator {{
        background-color: {BORDER};
        border: none;
    }}

    /* ========== 工具提示 ========== */
    QToolTip {{
        background-color: {BG_CARD};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER};
        border-radius: 6px;
        padding: 6px 10px;
        font-size: 12px;
    }}
    """