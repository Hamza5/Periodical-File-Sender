import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QTableWidgetItem

from GUI import Ui_MainWindow
from email_dialog import Ui_AddEmailDialog
from scheduling import EmailMessage, SendingTimeMonitor


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
        self.editPushButton.clicked.connect(self.edit_email_task)
        self.removePushButton.clicked.connect(self.remove_email_task)
        self.filesTableWidget.itemSelectionChanged.connect(
            lambda: self.editPushButton.setEnabled(bool(self.filesTableWidget.selectedIndexes()))
            or self.removePushButton.setEnabled(bool(self.filesTableWidget.selectedIndexes()))
            or self.sendPushButton.setEnabled(bool(self.filesTableWidget.selectedIndexes()))
        )
        self.send_monitor = SendingTimeMonitor(self.serverAddressLineEdit.text(), self.serverPortSpinBox.value(),
                                               self.usernameLineEdit.text(), self.passwordLineEdit.text(),
                                               self.tlsCheckBox.isChecked())
        self.show()

    @staticmethod
    def _period_symbol(index):
        return ['m', 'h', 'd', 'w', 'M', 'Y'][index]

    def add_email_task(self):
        email_dialog = EmailDialog(self)

        def email_dialog_accepted():
            to = email_dialog.toLineEdit.text()
            subject = email_dialog.subjectLineEdit.text()
            content = email_dialog.bodyPlainTextEdit.toPlainText()
            attachment_path = email_dialog.filePathLlineEdit.text()
            sender = self.senderNameLineEdit.text() + ' <' + self.senderEmailLineEdit.text() + '>'
            email_message = EmailMessage(sender, to, subject, content, attachment_path,
                                         self._period_symbol(email_dialog.periodComboBox.currentIndex()),
                                         email_dialog.periodSpinBox.value())
            self.send_monitor.set_next_send(email_message)
            to_item = DataQTableWidgetItem(to)
            subject_item = DataQTableWidgetItem(subject, email_message)
            schedule_item = DataQTableWidgetItem(self.tr('Every') + ' ' + str(email_dialog.periodSpinBox.value()) + ' '
                                                 + email_dialog.periodComboBox.currentText())
            items = [subject_item, to_item, schedule_item, DataQTableWidgetItem(),
                     DataQTableWidgetItem(str(email_message.next_send))]
            self.filesTableWidget.insertRow(self.filesTableWidget.rowCount())
            for i, item in enumerate(items):
                self.filesTableWidget.setItem(self.filesTableWidget.rowCount()-1, i, item)

        email_dialog.accepted.connect(email_dialog_accepted)
        email_dialog.exec()

    def remove_email_task(self):
        self.filesTableWidget.removeRow(self.filesTableWidget.selectedIndexes()[0].row())

    def edit_email_task(self):
        pass


app = QApplication(sys.argv)
window = MainWindow()
sys.exit(app.exec())
