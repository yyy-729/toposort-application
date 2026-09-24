"""应用的统一视觉主题。"""

from PySide6.QtGui import QColor, QPalette


def make_palette(dark: bool) -> QPalette:
    """为弹出列表和对话框设置明确的颜色，避免跟随系统出现黑底黑字。"""
    palette = QPalette()
    window = "#151C2D" if dark else "#F4F7FC"
    surface = "#1D273B" if dark else "#FFFFFF"
    text = "#EBF1FB" if dark else "#18243B"
    muted = "#A7B6CE" if dark else "#66758D"
    highlight = "#657DF5" if dark else "#DDE5FF"
    selected_text = "#FFFFFF" if dark else "#1B3473"
    palette.setColor(QPalette.ColorRole.Window, QColor(window))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(text))
    palette.setColor(QPalette.ColorRole.Base, QColor(surface))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(window))
    palette.setColor(QPalette.ColorRole.Text, QColor(text))
    palette.setColor(QPalette.ColorRole.Button, QColor(surface))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(text))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(highlight))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(selected_text))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(surface))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(text))
    palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(muted))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(muted))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(muted))
    return palette


APP_STYLESHEET = """
* {
    font-family: "Microsoft YaHei", "SimHei", "Segoe UI";
    font-size: 13px;
    color: #172033;
}

QMainWindow, QWidget#appRoot {
    background: #F3F6FB;
}

QFrame[role="panel"] {
    background: #FFFFFF;
    border: 1px solid #E4EAF2;
    border-radius: 14px;
}

QFrame[role="statCard"] {
    background: #F8FAFD;
    border: 1px solid #E8EDF5;
    border-radius: 10px;
}

QLabel#appTitle {
    font-size: 23px;
    font-weight: 700;
    color: #14213D;
}

QLabel#appSubtitle {
    font-size: 12px;
    color: #68758B;
}

QLabel#logoBadge {
    color: white;
    background: #3157D5;
    border-radius: 20px;
    font-size: 23px;
    font-weight: 700;
    qproperty-alignment: AlignCenter;
}

QLabel#statusPill {
    color: #2452C9;
    background: #EAF0FF;
    border: 1px solid #C9D7FF;
    border-radius: 12px;
    padding: 5px 11px;
    font-weight: 600;
}

QLabel#panelTitle {
    font-size: 16px;
    font-weight: 700;
    color: #172033;
}

QLabel#panelSubtitle, QLabel#mutedText {
    color: #758197;
    font-size: 12px;
}

QLabel#statValue {
    font-size: 20px;
    font-weight: 700;
    color: #2446B8;
}

QLabel#statTitle {
    color: #718096;
    font-size: 11px;
}

QPlainTextEdit {
    background: #F8FAFD;
    border: 1px solid #DDE5F0;
    border-radius: 10px;
    padding: 10px;
    selection-background-color: #BFD0FF;
    font-family: "Cascadia Mono", "Consolas", "Microsoft YaHei UI";
    font-size: 13px;
}

QPlainTextEdit:focus {
    border: 1px solid #5C7CFA;
    background: #FFFFFF;
}

QPushButton {
    background: #FFFFFF;
    border: 1px solid #D6DEEA;
    border-radius: 9px;
    padding: 8px 14px;
    font-weight: 600;
}

QPushButton:hover {
    background: #F4F7FC;
    border-color: #AAB8CF;
}

QPushButton:pressed {
    background: #E9EEF7;
}

QPushButton:disabled {
    color: #A6B0C0;
    background: #F5F7FA;
    border-color: #E5EAF0;
}

QPushButton[role="primary"] {
    color: #FFFFFF;
    background: #3157D5;
    border: 1px solid #3157D5;
    padding: 9px 20px;
}

QPushButton[role="primary"]:hover {
    background: #274AC2;
    border-color: #274AC2;
}

QSpinBox {
    background: #FFFFFF;
    border: 1px solid #D6DEEA;
    border-radius: 8px;
    padding: 6px 9px;
    min-width: 85px;
}

QComboBox {
    background: #FFFFFF;
    border: 1px solid #D6DEEA;
    border-radius: 8px;
    padding: 6px 10px;
    min-width: 92px;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QCheckBox {
    color: #526078;
    spacing: 6px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
}

QTabWidget::pane {
    border: 1px solid #DDE5F0;
    border-radius: 9px;
    background: #F8FAFD;
    top: -1px;
}

QTabBar::tab {
    color: #68758B;
    background: transparent;
    padding: 7px 13px;
    border-bottom: 2px solid transparent;
}

QTabBar::tab:selected {
    color: #3157D5;
    border-bottom: 2px solid #3157D5;
    font-weight: 700;
}

QLabel[role="hint"] {
    color: #506078;
    background: #F3F6FB;
    border: 1px solid #E1E8F2;
    border-radius: 9px;
    padding: 9px;
}

QLabel[role="notice"] {
    color: #8A6116;
    background: #FFF8E6;
    border: 1px solid #F4D58D;
    border-radius: 9px;
    padding: 9px;
}

QProgressBar {
    border: none;
    background: #E7ECF4;
    border-radius: 3px;
    max-height: 6px;
}

QProgressBar::chunk {
    background: #4F6FE8;
    border-radius: 3px;
}

QSplitter::handle {
    background: transparent;
    width: 8px;
}

QStatusBar {
    background: #FFFFFF;
    border-top: 1px solid #E4EAF2;
    color: #667085;
}

QMenuBar {
    background: #FFFFFF;
    border-bottom: 1px solid #E4EAF2;
}

QMenuBar::item:selected, QMenu::item:selected {
    background: #EAF0FF;
}

QMenu {
    background: #FFFFFF;
    border: 1px solid #DDE5F0;
    padding: 5px;
}

QToolBar {
    background: #FFFFFF;
    border: none;
    spacing: 4px;
}

QToolButton {
    background: transparent;
    border: none;
    border-radius: 6px;
    padding: 4px;
}

QToolButton:hover {
    background: #EEF2F8;
}

QFrame#heroBar {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #172B52, stop:1 #314B94);
    border: 1px solid #3F59A1;
    border-radius: 18px;
}

QFrame#heroBar QLabel#appTitle {
    color: #FFFFFF;
    font-size: 24px;
}

QFrame#heroBar QLabel#appSubtitle, QFrame#heroBar QLabel#heroEyebrow {
    color: #C5D3F4;
}

QFrame#heroBar QLabel#heroEyebrow {
    font-size: 10px;
    font-weight: 700;
}

QFrame#heroBar QLabel#logoBadge {
    background: #7086FF;
    border-radius: 23px;
}

QFrame#heroBar QLabel#statusPill {
    color: #274381;
    background: #EFF3FF;
    border: 1px solid #D5DEFF;
    border-radius: 11px;
    padding: 6px 12px;
}

QPushButton[role="header"] {
    color: #F7F9FF;
    background: rgba(255, 255, 255, 0.13);
    border: 1px solid rgba(255, 255, 255, 0.25);
}

QPushButton[role="header"]:hover {
    background: rgba(255, 255, 255, 0.22);
}

QFrame#commandBar {
    background: #FFFFFF;
    border: 1px solid #E3EAF5;
    border-radius: 14px;
}

QFrame[role="panel"] {
    border-color: #E2E9F5;
    border-radius: 16px;
}

QFrame[role="statCard"] {
    background: #F7F9FD;
    border-color: #E5EBF5;
    border-radius: 12px;
}

QPushButton[role="primary"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #536EED, stop:1 #3F59D7);
    border: 1px solid #4A63DE;
    border-radius: 10px;
}

QPushButton[role="primary"]:hover {
    background: #3D57CD;
}

QComboBox QAbstractItemView {
    color: #18243B;
    background: #FFFFFF;
    border: 1px solid #D8E2F1;
    selection-background-color: #E4EBFF;
    selection-color: #233C7D;
    outline: 0;
    padding: 4px;
}

QComboBox QAbstractItemView::item {
    min-height: 30px;
    padding: 5px 10px;
}

QComboBox QAbstractItemView::item:selected {
    color: #233C7D;
    background: #E4EBFF;
}

QDialog, QMessageBox {
    color: #18243B;
    background: #FFFFFF;
}

QDialog QLabel, QMessageBox QLabel {
    color: #18243B;
}

QToolTip {
    color: #18243B;
    background: #FFFFFF;
    border: 1px solid #D8E2F1;
    padding: 5px;
}

QLabel[role="graphGuide"] {
    color: #8794AA;
    font-size: 11px;
    padding: 2px 0;
}

QDialog#aboutDialog {
    background: #FFFFFF;
}

QLabel#aboutTitle {
    color: #17233C;
    font-size: 23px;
    font-weight: 700;
}

QLabel#aboutVersion {
    color: #586B8E;
    font-size: 12px;
}

QLabel#aboutDescription {
    color: #42516A;
    font-size: 14px;
}
"""


DARK_STYLESHEET = APP_STYLESHEET + """
* {
    color: #E6EDF7;
}

QMainWindow, QWidget#appRoot {
    background: #0B1220;
}

QFrame[role="panel"] {
    background: #111827;
    border-color: #263348;
}

QFrame[role="statCard"] {
    background: #172033;
    border-color: #2A3950;
}

QLabel#appTitle, QLabel#panelTitle {
    color: #F5F7FB;
}

QLabel#appSubtitle, QLabel#panelSubtitle, QLabel#mutedText, QLabel#statTitle {
    color: #93A4BC;
}

QLabel#statValue {
    color: #83A6FF;
}

QLabel#statusPill {
    color: #BFD0FF;
    background: #172A55;
    border-color: #3157D5;
}

QPlainTextEdit {
    color: #E6EDF7;
    background: #0F172A;
    border-color: #2B3A50;
    selection-background-color: #3157D5;
}

QPlainTextEdit:focus {
    background: #111C30;
    border-color: #6687F5;
}

QPushButton, QComboBox, QSpinBox {
    color: #DCE5F3;
    background: #172033;
    border-color: #33445D;
}

QPushButton:hover, QComboBox:hover, QSpinBox:hover {
    background: #1D2A40;
    border-color: #536782;
}

QPushButton:disabled {
    color: #64748B;
    background: #111827;
    border-color: #263348;
}

QPushButton[role="primary"] {
    color: #FFFFFF;
    background: #4568E6;
    border-color: #4568E6;
}

QLabel[role="hint"] {
    color: #B6C2D4;
    background: #172033;
    border-color: #2B3A50;
}

QLabel[role="notice"] {
    color: #F8D98A;
    background: #302614;
    border-color: #665127;
}

QCheckBox {
    color: #B6C2D4;
}

QTabWidget::pane {
    border-color: #2B3A50;
    background: #0F172A;
}

QTabBar::tab {
    color: #93A4BC;
}

QTabBar::tab:selected {
    color: #83A6FF;
    border-bottom-color: #6687F5;
}

QStatusBar, QMenuBar, QMenu, QToolBar {
    color: #DCE5F3;
    background: #111827;
    border-color: #263348;
}

QMenuBar::item:selected, QMenu::item:selected, QToolButton:hover {
    background: #1D2A40;
}

QToolButton {
    color: #DCE5F3;
}

QFrame#commandBar {
    background: #1D273B;
    border-color: #34435D;
}

QFrame#heroBar {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #192849, stop:1 #273C79);
    border-color: #405787;
}

QComboBox QAbstractItemView {
    color: #EBF1FB;
    background: #1D273B;
    border-color: #465772;
    selection-background-color: #40579B;
    selection-color: #FFFFFF;
}

QComboBox QAbstractItemView::item:selected {
    color: #FFFFFF;
    background: #40579B;
}

QDialog, QMessageBox {
    color: #EBF1FB;
    background: #1D273B;
}

QDialog QLabel, QMessageBox QLabel {
    color: #EBF1FB;
}

QToolTip {
    color: #EBF1FB;
    background: #1D273B;
    border-color: #465772;
}

QLabel[role="graphGuide"] {
    color: #9EACC3;
}

QDialog#aboutDialog {
    background: #1D273B;
}

QLabel#aboutTitle, QLabel#aboutDescription {
    color: #EBF1FB;
}

QLabel#aboutVersion {
    color: #A9B9D2;
}
"""
