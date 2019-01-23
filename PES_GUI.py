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
        self.filesTableWidget.itemSelectionChanged.connect(self.preview_email)
        self.send_monitor = SendingTimeMonitor(self.serverAddressLineEdit.text(), self.serverPortSpinBox.value(),
                                               self.usernameLineEdit.text(), self.passwordLineEdit.text(),
                                               self.tlsCheckBox.isChecked())
        self.show()

    def _get_info_as_items(self, email_dialog):
        to = email_dialog.toLineEdit.text()
        subject = email_dialog.subjectLineEdit.text()
        content = email_dialog.bodyPlainTextEdit.toPlainText()
        attachment_path = email_dialog.filePathLlineEdit.text()
        sender = self.senderNameLineEdit.text() + ' <' + self.senderEmailLineEdit.text() + '>'
        email_message = EmailMessage(sender, to, subject, content, attachment_path,
                                     ['m', 'h', 'd', 'w', 'M', 'Y'][email_dialog.periodComboBox.currentIndex()],
                                     email_dialog.periodSpinBox.value())
        self.send_monitor.set_next_send(email_message)
        to_item = DataQTableWidgetItem(to)
        subject_item = DataQTableWidgetItem(subject, email_message)
        schedule_item = DataQTableWidgetItem(self.tr('Every') + ' ' + str(email_dialog.periodSpinBox.value()) + ' '
                                             + email_dialog.periodComboBox.currentText())
        return [subject_item, to_item, schedule_item, DataQTableWidgetItem(),
                DataQTableWidgetItem(str(email_message.next_send))]

    def add_email_task(self):
        email_dialog = EmailDialog(self)

        def email_dialog_accepted():
            items = self._get_info_as_items(email_dialog)
            self.filesTableWidget.insertRow(self.filesTableWidget.rowCount())
            for i, item in enumerate(items):
                self.filesTableWidget.setItem(self.filesTableWidget.rowCount()-1, i, item)

        email_dialog.accepted.connect(email_dialog_accepted)
        email_dialog.exec()

    def remove_email_task(self):
        self.filesTableWidget.removeRow(self.filesTableWidget.selectedIndexes()[0].row())

    def edit_email_task(self):
        email_dialog = EmailDialog(self)
        selected_index = self.filesTableWidget.selectedIndexes()[0].row()
        message = self.filesTableWidget.item(selected_index, 0).data
        assert isinstance(message, EmailMessage)
        email_dialog.setWindowTitle(self.tr('Edit a task'))
        email_dialog.toLineEdit.setText(message['To'])
        email_dialog.subjectLineEdit.setText(message['Subject'])
        email_dialog.bodyPlainTextEdit.setPlainText(message.get_content())
        email_dialog.filePathLlineEdit.setText(message.attachment_path)
        email_dialog.periodSpinBox.setValue(message.time_count)
        email_dialog.periodComboBox.setCurrentIndex(['m', 'h', 'd', 'w', 'M', 'Y'].index(message.time_unit))

        def email_dialog_accepted():
            items = self._get_info_as_items(email_dialog)
            for i, item in enumerate(items):
                self.filesTableWidget.setItem(selected_index, i, item)

        email_dialog.accepted.connect(email_dialog_accepted)
        email_dialog.exec()

    def preview_email(self):
        if self.filesTableWidget.selectedIndexes():
            selected_index = self.filesTableWidget.selectedIndexes()[0].row()
            message = self.filesTableWidget.item(selected_index, 0).data
            assert isinstance(message, EmailMessage)
            self.emailGroupBox.setEnabled(True)
            self.toLineEdit.setText(message['To'])
            self.subjectLineEdit.setText(message['Subject'])
            self.bodyPlainTextEdit.setPlainText(message.get_content())
            self.attachmentLineEdit.setText(message.attachment_path)
        else:
            self.emailGroupBox.setEnabled(False)
            self.toLineEdit.setText('')
            self.subjectLineEdit.setText('')
            self.bodyPlainTextEdit.setPlainText('')
            self.attachmentLineEdit.setText('')


app = QApplication(sys.argv)
window = MainWindow()
sys.exit(app.exec())
