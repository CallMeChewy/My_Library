from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QPushButton,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSpacerItem,
    QStatusBar,
    QSizePolicy,
    QDialog,
)
from PySide6.QtGui import QPalette, QColor, QIcon, QPixmap, QFont, QMouseEvent, QCursor
from PySide6.QtCore import Qt, QEvent, QPoint, QSize


class CustomWindow(QMainWindow):
    def __init__(self, title, central_widget=None):
        super().__init__()

        self.setWindowTitle(title)
        self.setWindowFlags(Qt.FramelessWindowHint)

        # Create custom title bar
        self.title_bar = CustomTitleBar(self, title)

        # Create status bar and set it separately from the central widget
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("background-color: #780000; color: white;")
        self.setStatusBar(self.status_bar)

        # Create a widget for the title bar and set its background color
        self.title_bar_widget = QWidget()
        self.title_bar_widget.setStyleSheet("background-color: #780000;")
        self.title_bar_layout = QVBoxLayout()
        self.title_bar_widget.setLayout(self.title_bar_layout)

        # Add the custom title bar to the title bar widget
        self.title_bar_layout.addWidget(self.title_bar)

        # Set the title bar widget as the QMainWindow's menu bar
        self.setMenuWidget(self.title_bar_widget)

        # Add the passed widget to the layout
        if central_widget:
            self.setCentralWidget(central_widget)

        self.setMouseTracking(True)
        self.resize_origin = QPoint()

    def get_content_widget(self):
        return self.centralWidget()

    def get_status_bar(self):
        return self.status_bar

    def event(self, event):
        if (
            event.type() == QEvent.MouseButtonPress
            and event.buttons() == Qt.LeftButton
            and self.status_bar.underMouse()
        ):
            self.resize_origin = event.position()

        if (
            event.type() == QEvent.MouseMove
            and event.buttons() == Qt.LeftButton
            and self.resize_origin is not None
        ):
            delta = event.position() - self.resize_origin
            new_width = self.width() + delta.x()
            new_height = self.height() + delta.y()

            screen_size = QApplication.primaryScreen().availableSize()
            new_x = self.x() + new_width
            new_y = self.y() + new_height

            if new_x > screen_size.width():
                new_width = screen_size.width() - self.x()
            if new_y > screen_size.height():
                new_height = screen_size.height() - self.y()

            self.resize(new_width, new_height)
            self.resize_origin = event.position()

        if event.type() == QEvent.MouseButtonRelease:
            self.resize_origin = None

        return super().event(event)


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)

        self.setStyleSheet("background-color: #780000;")

        self.label = QLabel(
            "Another Intuitive Product\nfrom the folks at\nBowersWorld.com"
        )
        self.label.setStyleSheet("color: #ffd200; font: bold 24px; text-align: center;")
        self.label.setAlignment(Qt.AlignCenter)

        pixmap = QPixmap("Assets/BowersWorld.png").scaled(170, 170, Qt.KeepAspectRatio)

        self.icon_label = QLabel()
        self.icon_label.setPixmap(pixmap)

        self.copyright_label = QLabel("\u00A9")
        self.copyright_label.setContentsMargins(0, 160, 0, 0)
        self.copyright_label.setStyleSheet(
            "color: #ffd200; font: bold 24px; text-align: center;"
        )

        self.icon_layout = QHBoxLayout()
        self.icon_layout.addWidget(QLabel("   "))
        self.icon_layout.addWidget(self.icon_label)
        self.icon_layout.addWidget(self.copyright_label)

        self.icon_layout.insertStretch(0, 1)
        self.icon_layout.insertStretch(4, 1)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.setLayout(self.layout)

        self.layout.addWidget(self.label)
        self.layout.addLayout(self.icon_layout)

    def showEvent(self, event):
        if self.parent() is not None:
            parent_rect = self.parent().frameGeometry()
            self.move(parent_rect.center() - self.rect().center())
        super().showEvent(event)


class IconLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.about_dialog = AboutDialog(self.window())
        self.setMouseTracking(True)

    def enterEvent(self, e):
        if e.type() == QEvent.Enter:
            self.about_dialog.move(QCursor.pos())
            self.about_dialog.show()

    def leaveEvent(self, e):
        if e.type() == QEvent.Leave:
            self.about_dialog.hide()


class CustomTitleBar(QWidget):
    def __init__(self, parent, title):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(24)
        self.setStyleSheet("background-color: #780000; color: white;")

        self.draggable = False
        self.draggable_offset = QPoint()

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.icon_label = IconLabel(self)
        self.icon_label.setPixmap(
            QPixmap("Assets/icon.png").scaled(30, 30, Qt.KeepAspectRatio)
        )

        self.title_label = QLabel(self)
        self.title_label.setText(title)
        self.title_label.setStyleSheet("font: 12pt Arial;")

        self.spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        # Tooltip styles for the buttons
        tooltip_stylesheet = """
        QToolTip {
            font-size: 16px;
        }
        """

        self.min_button = QPushButton(self)
        pixmap = QPixmap("Assets/hide.png").scaled(34, 34, Qt.KeepAspectRatio)
        self.min_button.setIcon(QIcon(pixmap))
        self.min_button.setIconSize(QSize(34, 34))
        self.min_button.setFixedSize(28, 28)
        self.min_button.clicked.connect(self.parent.showMinimized)

        self.min_button.setStyleSheet(
            """
        QPushButton {
            background-color: none;
        }
        QPushButton:hover {
            background-color: #FFFFFF;
        }
        QPushButton:pressed {
            background-color: #800000;
        }
        """
            + tooltip_stylesheet
        )
        self.min_button.setToolTip("Hide")

        self.max_button = QPushButton(self)
        pixmap = QPixmap("Assets/Max.png").scaled(30, 30, Qt.KeepAspectRatio)
        self.max_button.setIcon(QIcon(pixmap))
        self.max_button.setIconSize(QSize(30, 30))
        self.max_button.setFixedSize(28, 28)
        self.max_button.clicked.connect(self.toggle_maximize)
        self.max_button.setStyleSheet(
            """
        QPushButton {
            background-color: none;
        }
        QPushButton:hover {
            background-color: #FFFFFF;
        }
        QPushButton:pressed {
            background-color: #800000;
        }
        """
            + tooltip_stylesheet
        )
        self.max_button.setToolTip("Max/Min")

        self.exit_button = QPushButton(self)
        pixmap = QPixmap("Assets/exit.png").scaled(30, 30)
        self.exit_button.setIcon(QIcon(pixmap))
        self.exit_button.setIconSize(QSize(30, 24))
        self.exit_button.setFixedSize(30, 24)
        self.exit_button.clicked.connect(self.parent.close)
        self.exit_button.setStyleSheet(
            """
        QPushButton {s
            background-color: none;
        }
        QPushButton:hover {
            background-color: #FFFFFF;
        }
        QPushButton:pressed {
            background-color: #800000;
        }
        """
            + tooltip_stylesheet
        )
        self.exit_button.setToolTip("Exit")

        self.layout.addWidget(self.icon_label)
        self.layout.addWidget(self.title_label)
        self.layout.addItem(self.spacer)
        self.layout.addWidget(self.min_button)
        self.layout.addWidget(self.max_button)
        self.layout.addWidget(self.exit_button)

        self.normal_size = self.parent.size()

    def toggle_maximize(self):
        if self.parent.isFullScreen():
            self.parent.showNormal()
            self.parent.resize(self.normal_size)
        else:
            self.normal_size = self.parent.size()
            self.parent.showFullScreen()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.draggable = True
            self.draggable_offset = (
                event.globalPosition().toPoint() - self.parent.frameGeometry().topLeft()
            )

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.draggable:
            new_position = event.globalPosition().toPoint() - self.draggable_offset
            self.parent.move(new_position)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.draggable = False

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.toggle_maximize()


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    # Increase size of tool tips
    app.setStyleSheet(
        """
    QToolTip {
        font-size: px;
    }
    """
    )

    window = CustomWindow("Test Window")
    window.showMaximized()
    sys.exit(app.exec())
