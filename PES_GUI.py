import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QTableWidgetItem

from GUI import Ui_MainWindow
from email_dialog import Ui_AddEmailDialog


class DataQTableWidgetItem(QTableWidgetItem):

    def __init__(self, text='', data=None):
        assert isinstance(text, str)
        super().__init__(text)
        self.data = data


class EmailDialog(QDialog, Ui_AddEmailDialog):

    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)
        self.show()


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.addPushButton.clicked.connect(self.add_email_task)
        self.show()

    def add_email_task(self):
        email_dialog = EmailDialog(self)

        def to_symbol(index):
            return ['m', 'h', 'd', 'w', 'M', 'Y'][index]

        def email_dialog_accepted():
            to = email_dialog.toLineEdit.text()
            subject = email_dialog.subjectLineEdit.text()
            content = email_dialog.bodyPlainTextEdit.toPlainText()
            attachment_path = email_dialog.filePathLlineEdit.text()
            to_item = DataQTableWidgetItem(to, to)
            subject_item = DataQTableWidgetItem(subject, (subject, content, attachment_path))
            schedule_item = DataQTableWidgetItem(self.tr('Every') + ' ' + str(email_dialog.periodSpinBox.value()) + ' '
                                                 + email_dialog.periodComboBox.currentText(),
                                                 [email_dialog.periodSpinBox.value(),
                                                  to_symbol(email_dialog.periodComboBox.currentIndex())])
            items = [subject_item, to_item, schedule_item, DataQTableWidgetItem(), DataQTableWidgetItem()]
            self.filesTableWidget.insertRow(self.filesTableWidget.rowCount())
            for i, item in enumerate(items):
                self.filesTableWidget.setItem(self.filesTableWidget.rowCount()-1, i, item)

        email_dialog.accepted.connect(email_dialog_accepted)
        email_dialog.exec()


app = QApplication(sys.argv)
window = MainWindow()
sys.exit(app.exec())
