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
