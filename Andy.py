import sys
import os
import sqlite3
import webbrowser
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QScrollArea,
    QGridLayout,
    QLabel,
    QVBoxLayout,
    QComboBox,
    QHBoxLayout,
    QSizePolicy,
    QSpacerItem,
    QMessageBox,
    QLineEdit,
    QListView,
    QToolTip,
)
from PySide6.QtGui import QPixmap, QFont, QPen, QPainter
from PySide6.QtCore import (
    Qt,
    QEvent,
    QTimer,
    QStringListModel,
)
from CustomWindow import CustomWindow


class ToolTipListView(QListView):
    def __init__(self, parent=None):
        super().__init__(parent)

    def viewportEvent(self, event):
        if event.type() == QEvent.ToolTip:
            index = self.indexAt(event.pos())
            if index.isValid():
                QToolTip.showText(event.globalPos(), index.data(), self)
            else:
                QToolTip.hideText()
                event.ignore()
            return True
        return super().viewportEvent(event)


class HoverHighlightWidget(QWidget):
    def __init__(self, main_window, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_window = main_window
        self.setMouseTracking(True)
        self.hovered = False
        self.description = ""

    def enterEvent(self, event):
        self.hovered = True
        self.update()

    def leaveEvent(self, event):
        self.hovered = False
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.BookName = self.description
            self.main_window.getPDF(self.BookName)

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.hovered:
            painter = QPainter(self)
            painter.setPen(QPen(Qt.red, 8))
            painter.drawRect(self.rect())


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Placeholder values for ComboBoxes
        self.placeholders = [
            "Select a Category",
            "Select a Subject",
            "Select a Book Title",
            "Type Something Here",
        ]
        self.C_WAS = 0
        self.C_NOW = 0
        self.W_ITEM = 230
        self.W_BASE = 315
        self.books = False

        # Connect to the database
        self.conn = sqlite3.connect("Assets/my_library.db")
        self.c = self.conn.cursor()

        self.setMouseTracking(True)

        # Create the dropdowns and combobox
        self.box1_values = self.populate_box1()
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)

        self.main_layout = QHBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)  # Remove space around layout

        # Create comboboxes
        self.dropdowns_container = QWidget()
        self.dropdowns_container.setFixedWidth(300)
        self.main_layout.addWidget(self.dropdowns_container)
        self.dropdowns = QVBoxLayout(self.dropdowns_container)
        self.dropdowns.setContentsMargins(0, 0, 0, 0)  # Remove space around layout

        font = QFont("Aerial", 12)
        # font.setBold(True)  # Make the font bold
        heading = QLabel(
            "- - - O p t i o n s - - -  ", alignment=Qt.AlignmentFlag.AlignHCenter
        )
        heading.setFont(font)
        heading.setStyleSheet("color: #FCC419")  # ffd200")
        self.dropdowns.addWidget(heading)
        heading.setObjectName("heading")

        # Create a QFont object for the font size
        font = QFont()
        font.setPointSize(12)

        # Create comboboxes
        self.box1 = QComboBox()
        self.box1.setMaxVisibleItems(30)
        self.box1.setFont(font)
        view1 = ToolTipListView()
        view1.setFont(font)
        view1.setStyleSheet("QListView::item { height: 18px; }")
        view1.setTextElideMode(Qt.ElideRight)
        self.box1.setView(view1)
        self.reset(self.box1, 0)  # Set placeholder
        for category in self.box1_values:
            self.box1.addItem(category)
            self.box1.setItemData(self.box1.count() - 1, category, Qt.ToolTipRole)
        self.box1.currentTextChanged.connect(self.box1_callback)
        self.dropdowns.addWidget(self.box1)

        self.box2 = QComboBox()
        self.box2.setMaxVisibleItems(30)
        self.box2.setFont(font)
        view2 = ToolTipListView()
        view2.setFont(font)
        view2.setStyleSheet("QListView::item { height: 18px; }")
        view2.setTextElideMode(Qt.ElideRight)
        self.box2.setView(view2)
        self.reset(self.box2, 1)  # Set placeholder
        self.box2.currentTextChanged.connect(self.box2_callback)
        self.dropdowns.addWidget(self.box2)

        self.box3 = QComboBox()
        self.box3.setMaxVisibleItems(30)
        self.box3.setFont(font)
        view3 = ToolTipListView()
        view3.setFont(font)
        view3.setStyleSheet("QListView::item { height: 18px; }")
        view3.setTextElideMode(Qt.ElideRight)
        self.box3.setView(view3)
        self.reset(self.box3, 2)  # Set placeholder
        self.box3.currentTextChanged.connect(self.box3_callback)  # New connection
        self.dropdowns.addWidget(self.box3)

        # Increase the height of the QLineEdit
        self.line_edit = QLineEdit()
        self.line_edit.setMinimumHeight(18)  # Change this to adjust the height
        self.line_edit.setFont(font)  # This will increase the text size
        self.line_edit.installEventFilter(self)
        self.line_edit.setText("Type Something Here")  # Set the starting text

        # Increase the text size in the listbox
        self.list_view = ToolTipListView()
        self.list_view.setFont(font)  # This will increase the text size

        self.model = QStringListModel()
        self.list_view.setModel(self.model)
        self.line_edit.textChanged.connect(self.search_books)
        self.list_view.clicked.connect(self.item_clicked)

        self.dropdowns.addWidget(self.line_edit)
        self.dropdowns.addWidget(self.list_view)

        # Make the listbox expand to the status bar
        self.list_view.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        self.scroll_area = QScrollArea()
        self.main_layout.addWidget(self.scroll_area)

        self.scroll_widget = QWidget()
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)  # Make the scroll area resizable

        self.grid_layout = QGridLayout(self.scroll_widget)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)  # Remove space around layout

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.checkSize)  # Connect to checkSize method
        self.timer.start(100)  # Call checkSize every 2 seconds

    def reset(self, box, index):
        placeholder = self.placeholders[index]
        box.blockSignals(True)
        box.clear()
        box.addItem(placeholder)
        box.setCurrentIndex(0)
        box.blockSignals(False)

    def load_data(self):
        # Clear displayed widgets
        for i in reversed(range(self.grid_layout.count())):
            widget_to_remove = self.grid_layout.itemAt(i).widget()
            if widget_to_remove is not None:
                self.grid_layout.removeWidget(widget_to_remove)  # remove from layout
                widget_to_remove.setParent(None)  # remove from gui

        # Display selected widgets
        for i, (title,) in enumerate(self.books):
            image_path = os.path.join("Anderson eBooks\\Covers", title + ".png")
            item_widget = HoverHighlightWidget(self)

            item_widget.description = title
            item_layout = QHBoxLayout(item_widget)
            item_layout.setContentsMargins(3, 3, 5, 5)  # Remove space around the layout

            image_label = QLabel()
            pixmap = QPixmap(image_path)
            if pixmap.isNull():
                image_label.setText("Failed to load image")
            else:
                pixmap = pixmap.scaled(175 * 0.60, 225 * 0.60, Qt.KeepAspectRatio)
                image_label.setPixmap(pixmap)
            item_layout.addWidget(image_label)

            description_label = QLabel(title)
            font = QFont("Arial", 11)
            description_label.setFont(font)
            description_label.setWordWrap(True)
            description_label.setFixedSize(175 * 0.60, 225 * 0.60)  # Fixed size desc
            item_layout.addWidget(description_label)

            cols = self.C_NOW
            self.grid_layout.addWidget(item_widget, i // cols, i % cols)

        # Add spacers to push all widgets to the top left
        if self.books:
            self.grid_layout.addItem(
                QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding),
                i // cols + 1,
                i % cols,
            )
            self.grid_layout.addItem(
                QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding),
                i // cols,
                i % cols + 1,
            )

    def populate_box1(self):
        self.c.execute("SELECT DISTINCT category FROM categories ORDER BY category ASC")
        categories = self.c.fetchall()
        self.box1_values = []
        for category in categories:
            self.box1_values.append(category[0])
        return self.box1_values

    def box1_callback(self, choice):
        self.reset(self.box2, 1)
        self.reset(self.box3, 2)
        self.line_edit.clear()
        self.line_edit.setText("Type Something Here")

        # Fetch the subjects for category and populate box2
        self.c.execute(
            "SELECT DISTINCT subject FROM subjects WHERE category_id = (SELECT id FROM categories WHERE category = ?)",
            (choice,),
        )
        subjects = self.c.fetchall()
        self.box2.blockSignals(True)
        for subject in subjects:
            self.box2.addItem(subject[0])
        self.box2.blockSignals(False)

    def box2_callback(self, choice):
        self.reset(self.box3, 2)
        self.line_edit.clear()
        self.line_edit.setText("Type Something Here")
        # Fetch the books for subject and populate box3
        self.c.execute(
            "SELECT title FROM books WHERE subject_id = (SELECT id FROM subjects WHERE subject = ?)",
            (choice,) if isinstance(choice, str) else choice,
        )
        self.books = self.c.fetchall()
        self.box3.blockSignals(True)
        for book in self.books:
            self.box3.addItem(book[0])
        self.box3.blockSignals(False)
        self.load_data()

    def box3_callback(self, choice):  # New method
        self.BookName = choice
        self.getPDF(self.BookName)

    def item_clicked(self, index):
        self.BookName = index.data()
        self.getPDF(self.BookName)

    def getPDF(self, BookName):
        if BookName:
            image_path = os.path.join("Anderson eBooks\\Covers", BookName + ".png")
            pdf_path = os.path.join("Anderson eBooks", BookName + ".pdf")

            msgBox = QMessageBox()
            msgBox.setWindowTitle("Selected Book")
            msgBox.setText("Would you like to read:\n\n" + BookName)
            msgBox.setIconPixmap(QPixmap(image_path))
            msgBox.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ok)
            msgBox.setDefaultButton(QMessageBox.Ok)

            # Set the stylesheet
            msgBox.setStyleSheet(
                """
                QLabel{
                    font-size: 24px;
                }
                QPushButton{
                    min-height: 30px;
                    min-width: 70px;
                    font-size: 16px;
                }
            """
            )

            returnValue = msgBox.exec()
            if returnValue == QMessageBox.Ok:
                webbrowser.open_new(pdf_path)

    def search_books(self, search_term):
        # Clear the list_view if there's no data in the entry
        if not search_term:
            self.model.setStringList([])
            return

        # Only load data if the length of search_term is greater than 1
        if len(search_term) > 1:
            self.c.execute(
                "SELECT title FROM books WHERE title LIKE ? ORDER BY title COLLATE NOCASE",
                ("%" + search_term + "%",),
            )
            self.books = self.c.fetchall()
            self.model.setStringList([title[0] for title in self.books])
            self.load_data()

    def eventFilter(self, source, event):
        if (source is self.line_edit) and (event.type() == QEvent.FocusIn):
            self.box3.clear()
            self.box1.setCurrentIndex(0)
            self.reset(self.box2, 1)
            self.reset(self.box3, 2)
            self.line_edit.setText("")
        return super(MainWindow, self).eventFilter(source, event)

    def checkSize(self):
        # print("check")
        if self.C_WAS != self.C_NOW:
            # print("change", self.C_WAS, self.C_NOW)
            self.C_WAS = self.C_NOW
            if self.books:
                self.load_data()

    def resizeEvent(self, event):  # 14	Widget's size changed (QResizeEvent).
        super().resizeEvent(event)
        size = event.size()
        width = size.width()
        height = size.height()
        self.C_NOW = int((width - self.W_BASE) / self.W_ITEM)
        window.get_status_bar().showMessage(f"{width} x {height}  C:{self.C_NOW}")


# Start the application
app = QApplication(sys.argv)
app.setStyleSheet(
    """
    * {
        background-color: qlineargradient(spread:repeat, x1:1, y1:0, x2:1, y2:1, stop:0.00480769 rgba(3, 50, 76, 255), stop:0.293269 rgba(6, 82, 125, 255), stop:0.514423 rgba(8, 117, 178, 255), stop:0.745192 rgba(7, 108, 164, 255), stop:1 rgba(3, 51, 77, 255));
        color: #FFFFFF;
        border: none;
    }

    QComboBox::down-arrow {
        image: url(Assets/arrow.png);
    }

    QComboBox::item:hover, QListView::item:hover {
        border: 3px solid red;
    }
    QToolTip { 
        color: #ffffff; 
        border: none; font-size: 16px; 
    }

"""
)

main_window = MainWindow()
window = CustomWindow("Anderson's Library", main_window)
window.showMaximized()
sys.exit(app.exec())
