from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QTextEdit
)
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QIcon
import sys

class CustomTitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(30)
        self.setStyleSheet("background: #2a2a2a;")
        self._is_maximized = False

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)

        # Title
        self.title_label = QLabel("OSC-CY Editor")
        self.title_label.setStyleSheet("color: white; font-weight: bold;")
        layout.addWidget(self.title_label)
        layout.addStretch()

        # Minimize button
        self.btn_min = QPushButton()
        self.btn_min.setFixedSize(30, 24)
        self.btn_min.setIcon(QIcon("icons/minimize.svg"))
        self.btn_min.clicked.connect(self.parent().showMinimized)
        self.btn_min.setStyleSheet(self.button_style())
        layout.addWidget(self.btn_min)

        # Maximize/Restore button
        self.btn_max = QPushButton()
        self.btn_max.setFixedSize(30, 24)
        self.update_max_icon()
        self.btn_max.clicked.connect(self.toggle_max_restore)
        self.btn_max.setStyleSheet(self.button_style())
        layout.addWidget(self.btn_max)

        # Close button
        self.btn_close = QPushButton()
        self.btn_close.setFixedSize(30, 24)
        self.btn_close.setIcon(QIcon("icons/close.svg"))
        self.btn_close.clicked.connect(self.parent().close)
        self.btn_close.setStyleSheet(self.button_style(close=True))
        layout.addWidget(self.btn_close)

    def toggle_max_restore(self):
        if self._is_maximized:
            self.parent().showNormal()
            self._is_maximized = False
        else:
            self.parent().showMaximized()
            self._is_maximized = True
        self.update_max_icon()

    def update_max_icon(self):
        if self._is_maximized:
            self.btn_max.setIcon(QIcon("icons/restore.svg"))  # restore icon
        else:
            self.btn_max.setIcon(QIcon("icons/maximize.svg"))  # maximize icon

    def button_style(self, close=False):
        if close:
            return """
                QPushButton {
                    background: #900; border: none;
                }
                QPushButton:hover { background: #f00; }
                QPushButton:pressed { background: #800; }
            """
        return """
            QPushButton {
                background: #444; border: none;
            }
            QPushButton:hover { background: #555; }
            QPushButton:pressed { background: #666; }
        """

    # Dragging the window
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.parent().frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.parent().move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()