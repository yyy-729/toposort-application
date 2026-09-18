"""应用的统一视觉主题。"""

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
"""
