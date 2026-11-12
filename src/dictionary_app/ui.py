"""Qt window and background lookup worker."""
import sys
from PySide6.QtCore import QThread, Signal, Slot
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QApplication, QLabel, QLineEdit, QPushButton, QTextEdit, QVBoxLayout, QWidget
from .dictionary import DictionaryError, lookup_word


class LookupThread(QThread):
    result = Signal(str)

    def __init__(self, word: str, parent: QWidget):
        super().__init__(parent)
        self.word = word

    def run(self) -> None:
        try:
            result = lookup_word(self.word)
        except DictionaryError as exc:
            result = str(exc)
        self.result.emit(result)


class DictionaryWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.setWindowTitle("My Dictionary")
        self.resize(600, 500)
        layout = QVBoxLayout(self)
        title = QLabel("ENGLISH DICTIONARY")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.word_input = QLineEdit()
        self.word_input.setPlaceholderText("Enter a word...")
        self.word_input.setAccessibleName("Word to search")
        self.search_button = QPushButton("Search")
        self.result_box = QTextEdit()
        self.result_box.setReadOnly(True)
        self.result_box.setPlaceholderText("Your search results will appear here.")
        for widget in (title, self.word_input, self.search_button, self.result_box):
            layout.addWidget(widget)
        self.search_button.clicked.connect(self.search)
        self.word_input.returnPressed.connect(self.search)
        self.word_input.setFocus()

    @Slot()
    def search(self) -> None:
        if self.worker is not None:
            return
        word = self.word_input.text().strip()
        if not word:
            self.result_box.setPlainText("Please enter a word.")
            return
        self.search_button.setEnabled(False)
        self.word_input.setEnabled(False)
        self.search_button.setText("Searching...")
        self.result_box.setPlainText(f'Searching for "{word}"...')
        self.worker = LookupThread(word, self)
        self.worker.result.connect(self.result_box.setPlainText)
        self.worker.finished.connect(self.search_finished)
        self.worker.start()

    @Slot()
    def search_finished(self) -> None:
        self.worker.deleteLater()
        self.worker = None
        self.search_button.setEnabled(True)
        self.word_input.setEnabled(True)
        self.search_button.setText("Search")
        self.word_input.setFocus()

    def closeEvent(self, event: QCloseEvent) -> None:
        # Retain the running thread until its network request finishes.
        if self.worker is not None:
            event.ignore()
            self.hide()
            self.worker.finished.connect(self.close)
        else:
            event.accept()


def run() -> int:
    app = QApplication(sys.argv)
    window = DictionaryWindow()
    window.show()
    return app.exec()
