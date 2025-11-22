from PySide6.QtWidgets import QDialog, QApplication, QTableWidget, QTableWidgetItem, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QHeaderView, QMessageBox
from PySide6.QtCore import Qt, QTimer, QRect, QPoint
from PySide6.QtGui import QIcon, QTextOption
from pysideHelpers import CustomTitleBar
import os
import sys
import json

class ExitInterceptWindow(QWidget):
    EDGE_MARGIN = 10  # pixels for resize area

    def __init__(self, closeEventCall=None):
        super().__init__()
        self.closeEventCall = closeEventCall
        self._resizing = False
        self._resize_dir = None

        # Frameless
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setMouseTracking(True)

    def closeEvent(self, event):
        if self.closeEventCall:
            self.closeEventCall()
        else:
            save()
        event.accept()

    # Detect edges for resize
    def mouseMoveEvent(self, event):
        pos = event.position().toPoint()
        rect = self.rect()
        margin = self.EDGE_MARGIN

        left = pos.x() <= margin
        top = pos.y() <= margin
        right = pos.x() >= rect.width() - margin
        bottom = pos.y() >= rect.height() - margin

        # Determine cursor and resize direction
        if left and top:
            self.setCursor(Qt.SizeFDiagCursor)
            self._resize_dir = "top_left"
        elif right and bottom:
            self.setCursor(Qt.SizeFDiagCursor)
            self._resize_dir = "bottom_right"
        elif left and bottom:
            self.setCursor(Qt.SizeBDiagCursor)
            self._resize_dir = "bottom_left"
        elif right and top:
            self.setCursor(Qt.SizeBDiagCursor)
            self._resize_dir = "top_right"
        elif left:
            self.setCursor(Qt.SizeHorCursor)
            self._resize_dir = "left"
        elif right:
            self.setCursor(Qt.SizeHorCursor)
            self._resize_dir = "right"
        elif top:
            self.setCursor(Qt.SizeVerCursor)
            self._resize_dir = "top"
        elif bottom:
            self.setCursor(Qt.SizeVerCursor)
            self._resize_dir = "bottom"
        else:
            self.setCursor(Qt.ArrowCursor)
            self._resize_dir = None

        if self._resizing and self._resize_dir:
            self.resizeWindow(event.globalPosition().toPoint())

        super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self._resize_dir:
            self._resizing = True
            self._drag_start = event.globalPosition().toPoint()
            self._start_geom = self.geometry()
            event.accept()
        elif event.button() == Qt.LeftButton:
            # Allow window dragging anywhere else
            self._drag_start = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self._resizing = False
            event.accept()

    def mouseReleaseEvent(self, event):
        self._resizing = False
        self._resize_dir = None
        self.setCursor(Qt.ArrowCursor)

    def mouseMoveEvent(self, event):
        if self._resizing:
            self.resizeWindow(event.globalPosition().toPoint())
        elif event.buttons() & Qt.LeftButton:
            # Dragging window
            self.move(event.globalPosition().toPoint() - self._drag_start)
        else:
            super().mouseMoveEvent(event)
            # Detect edges for resize cursor
            self.updateCursor(event.position().toPoint())

    def updateCursor(self, pos):
        rect = self.rect()
        margin = self.EDGE_MARGIN

        left = pos.x() <= margin
        top = pos.y() <= margin
        right = pos.x() >= rect.width() - margin
        bottom = pos.y() >= rect.height() - margin

        # Check corners first (diagonal)
        if left and top:
            self.setCursor(Qt.SizeFDiagCursor)
            self._resize_dir = "top_left"
        elif right and bottom:
            self.setCursor(Qt.SizeFDiagCursor)
            self._resize_dir = "bottom_right"
        elif left and bottom:
            self.setCursor(Qt.SizeBDiagCursor)
            self._resize_dir = "bottom_left"
        elif right and top:
            self.setCursor(Qt.SizeBDiagCursor)
            self._resize_dir = "top_right"
        # Then check horizontal/vertical edges
        elif left:
            self.setCursor(Qt.SizeHorCursor)
            self._resize_dir = "left"
        elif right:
            self.setCursor(Qt.SizeHorCursor)
            self._resize_dir = "right"
        elif top:
            self.setCursor(Qt.SizeVerCursor)
            self._resize_dir = "top"
        elif bottom:
            self.setCursor(Qt.SizeVerCursor)
            self._resize_dir = "bottom"
        else:
            self.setCursor(Qt.ArrowCursor)
            self._resize_dir = None


    def resizeWindow(self, global_pos):
        geom = self._start_geom
        diff = global_pos - self._drag_start

        x, y, w, h = geom.x(), geom.y(), geom.width(), geom.height()

        if "left" in self._resize_dir:
            x += diff.x()
            w -= diff.x()
        if "right" in self._resize_dir:
            w += diff.x()
        if "top" in self._resize_dir:
            y += diff.y()
            h -= diff.y()
        if "bottom" in self._resize_dir:
            h += diff.y()

        self.setGeometry(QRect(x, y, w, h))


class MessageBoxInput(QDialog):
    def __init__(self, title="Enter Text", button1_text="OK", button2_text="Cancel"):
        super().__init__()
        self.setWindowTitle(title)
        self.result_text = None  # will hold the returned text

        # Text input
        self.text_edit = QTextEdit()
        self.text_edit.setFixedHeight(80)
        self.text_edit.setObjectName("RemoveTextInput")

        # Buttons
        self.button1 = QPushButton(button1_text)
        self.button2 = QPushButton(button2_text)
        self.button1.clicked.connect(self.accept_text)
        self.button2.clicked.connect(self.reject)
        self.button1.setObjectName("RemoveAcceptButton")
        self.button2.setObjectName("RemoveRejectButton")

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.button1)
        button_layout.addWidget(self.button2)

        layout = QVBoxLayout()
        layout.addWidget(self.text_edit)
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def accept_text(self):
        self.result_text = self.text_edit.toPlainText()
        self.accept()  # closes the dialog with QDialog.Accepted

editing_row = 0

def editor_save_to_data():
    global editing_row
    if editing_row >= 0 and editing_row < len(data["messages"]):
        current_text = editor.toPlainText()
        # Only overwrite if non-empty
        if current_text != "":
            data["messages"][editing_row]["text"] = current_text

    # Sync time for all rows
    for row in range(table.rowCount()):
        time_item = table.item(row, 1)
        if time_item:
            data["messages"][row]["time"] = time_item.text()


def on_message_clicked(row):
    editor_save_to_data()
    
    global editing_row
    editing_row = row

    button = table.cellWidget(row, 0)  # returns the QPushButton
    editor.setPlainText(button.text())
    print(f"row {row} clicked")

if os.path.exists("messages.json"):
    with open("messages.json", "r") as file:
        data = json.loads(file.read())
else:
    open("messages.json", "w").write('{"message": []}')
    with open("messages.json", "r") as file:
        data = json.loads(file.read())

def save():
    editor_save_to_data()
    with open("messages.json", "w") as file:
        file.write(json.dumps(data, indent=4))

def add_row_func():
    # Add a new entry to data first
    new_message = {"text": "New message", "time": 0}
    data["messages"].append(new_message)
    
    row = table.rowCount()
    table.insertRow(row)
    
    # Button for the message column
    button = QPushButton(new_message["text"])
    button.setStyleSheet("text-align: left;")
    button.clicked.connect(lambda checked, r=row: on_message_clicked(r))
    button.setObjectName("TablePushButtons")
    table.setCellWidget(row, 0, button)
    
    # Time column
    time_item = QTableWidgetItem(new_message["time"])
    time_item.setTextAlignment(Qt.AlignCenter)
    table.setItem(row, 1, time_item)

def remove_row_func():
    dlg = MessageBoxInput(title="Delete Row", button1_text="Delete", button2_text="Cancel")
    if dlg.exec() != QDialog.Accepted:
        return

    try:
        row_index = int(dlg.result_text) - 1  # user sees 1-based index
    except ValueError:
        msg = QMessageBox()
        msg.setWindowTitle("Warning")
        msg.setText("Value entered is not a number!")
        msg.setIcon(QMessageBox.Warning)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()
        return

    if row_index < 0 or row_index >= len(data["messages"]):
        msg = QMessageBox()
        msg.setWindowTitle("Warning")
        msg.setText("Value entered is not a valid row!")
        msg.setIcon(QMessageBox.Warning)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()
        return

    # Remove from both data and table
    data["messages"].pop(row_index)
    table.removeRow(row_index)

app = QApplication(sys.argv)

# Create table: 3 rows, 3 columns
window = ExitInterceptWindow()
window.resize(800, 400)

title_bar = CustomTitleBar(parent=window)

top_layout = QVBoxLayout()

top_layout.addWidget(title_bar)

layout = QHBoxLayout()
layout.setContentsMargins(5, 5, 5, 5)

table = QTableWidget(0, 2)
table.setHorizontalHeaderLabels(["Message", "Time"])
header = table.horizontalHeader()

table_h_scroll = table.horizontalScrollBar()
table_v_scroll = table.verticalScrollBar()
table_h_scroll.setSingleStep(2)  # smaller = slower scroll
table_v_scroll.setSingleStep(2)

table.setObjectName("TableWidget")

# Column 0: Message column expands
header.setSectionResizeMode(0, QHeaderView.Stretch)

# Column 1: Time column fixed
header.setSectionResizeMode(1, QHeaderView.Fixed)
table.setColumnWidth(1, 40)

# Fill table
for row, message in enumerate(data["messages"]):
    table.insertRow(row)
    
    # Create a push button for the message cell
    button = QPushButton(str(message["text"]))
    button.setStyleSheet("text-align: left;")  # left-align text like normal
    button.clicked.connect(lambda checked, r=row: on_message_clicked(r))
    button.setObjectName("TablePushButtons")
    table.setCellWidget(row, 0, button)
    

    # Time column (still a normal item, centered)
    time_item = QTableWidgetItem(str(message["time"]))
    time_item.setTextAlignment(Qt.AlignCenter)
    table.setItem(row, 1, time_item)

# Set column widths
table.setColumnWidth(0, 300)
table.setColumnWidth(1, 40)
table.setMinimumWidth(381)

editor = QTextEdit()
editor.setObjectName("MainEditor")
editor.setLineWrapMode(QTextEdit.NoWrap)       # disables automatic line wrapping
editor.setWordWrapMode(QTextOption.NoWrap)     # make sure word wrap is off

# Scrollbars
editor_h_scroll = editor.horizontalScrollBar()
editor_v_scroll = editor.verticalScrollBar()
editor_h_scroll.setSingleStep(2)  # smaller = slower scroll
editor_v_scroll.setSingleStep(2)

editor.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
editor.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

layout.addWidget(table)
layout.addWidget(editor)

toolbar = QVBoxLayout()
toolbar.setContentsMargins(0, 10, 0, 10)

save_button = QPushButton()
save_button.setFixedSize(35,35)
save_button.clicked.connect(save)
save_button.setIcon(QIcon("icons/disk.svg"))
save_button.setObjectName("SaveButton")
toolbar.addWidget(save_button, alignment=Qt.AlignHCenter)

add_row = QPushButton()
add_row.setFixedSize(35,35)
add_row.clicked.connect(add_row_func)
add_row.setIcon(QIcon("icons/add.svg"))
add_row.setObjectName("AddRowButton")
toolbar.addWidget(add_row, alignment=Qt.AlignHCenter)

remove_row = QPushButton()
remove_row.setFixedSize(35,35)
remove_row.clicked.connect(remove_row_func)
remove_row.setIcon(QIcon("icons/trash.svg"))
remove_row.setObjectName("RemoveRowButton")
toolbar.addWidget(remove_row, alignment=Qt.AlignHCenter)

toolbar.addStretch()

toolbar_widget = QWidget()
toolbar_widget.setLayout(toolbar)
toolbar_widget.setFixedWidth(45)
toolbar_widget.setObjectName("ToolbarWidget")
layout.addWidget(toolbar_widget)
del toolbar_widget

layout.setStretch(0, 2)  # table gets 3x space
layout.setStretch(1, 2)  # editor gets 2x space
layout.setStretch(2, 0)  # toolbar keeps its fixed size

layout_widget = QWidget()
layout_widget.setLayout(layout)
top_layout.addWidget(layout_widget)

window.setLayout(top_layout)

autosave_timer = QTimer()
autosave_timer.timeout.connect(editor_save_to_data)  # sync editor -> data
autosave_timer.start(100)  # 100 ms = 0.1s

with open("style.qss", "r") as f:
    app.setStyleSheet(f.read())

window.show()

sys.exit(app.exec())
