import sys
from functools import partial
from threading import Thread

from PyQt5.QtCore import pyqtSlot, pyqtSignal, QRegExp
from PyQt5.QtGui import QFont, QRegExpValidator
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QTableWidgetItem, QFileDialog, QMessageBox

from GUI import Ui_MainWindow
from email_dialog import Ui_AddEmailDialog
from scheduling import TimedEmailMessage, SendingTimeMonitor

ITALIC_FONT = QFont()
ITALIC_FONT.setItalic(True)
EMAIL_REGEXP = QRegExp(r'.+@[\w-]+\.\w+')


class DataQTableWidgetItem(QTableWidgetItem):

    def __init__(self, text='', data=None):
        assert isinstance(text, str)
        super().__init__(text)
        self.data = data


class EmailDialog(QDialog, Ui_AddEmailDialog):

    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)
        self.browsePushButton.clicked.connect(self.open_file_window)
        self.toLineEdit.setValidator(QRegExpValidator(EMAIL_REGEXP))
        self.show()

    def open_file_window(self):
        path = QFileDialog.getOpenFileName(self, self.tr('Choose a file'))[0]
        if path:
            self.filePathLlineEdit.setText(path)

    def accept(self):
        if self.toLineEdit.hasAcceptableInput():
            super().accept()
        else:
            QMessageBox.warning(self, self.tr('Error'), self.tr('The email address that you entered is invalid'))


class MainWindow(QMainWindow, Ui_MainWindow):

    email_sent = pyqtSignal(TimedEmailMessage)

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
        self.email_sent.connect(self.update_ui_after_send)
        self.sendPushButton.clicked.connect(self.send_email)
        self.showPasswordCheckBox.toggled.connect(lambda enabled:
                                                  self.passwordLineEdit.setEchoMode(self.passwordLineEdit.Normal)
                                                  if enabled else
                                                  self.passwordLineEdit.setEchoMode(self.passwordLineEdit.Password))
        self.tasksFilePushButton.clicked.connect(self.open_tasks_file_selection_window)
        self.send_monitor = SendingTimeMonitor(self.serverAddressLineEdit.text(), self.serverPortSpinBox.value(),
                                               self.usernameLineEdit.text(), self.passwordLineEdit.text(),
                                               self.tlsCheckBox.isChecked())
        self.show()

    def _recalculate_indices(self):
        for i in range(self.filesTableWidget.rowCount()):
            message = self.filesTableWidget.item(i, 0).data
            assert isinstance(message, TimedEmailMessage)
            message.index = i

    def _get_info_as_items(self, email_dialog):
        to = email_dialog.toLineEdit.text()
        subject = email_dialog.subjectLineEdit.text()
        content = email_dialog.bodyPlainTextEdit.toPlainText()
        attachment_path = email_dialog.filePathLlineEdit.text()
        sender = self.senderNameLineEdit.text() + ' <' + self.senderEmailLineEdit.text() + '>'
        email_message = TimedEmailMessage(sender, to, subject, content, attachment_path,
                                          ['m', 'h', 'd', 'w', 'M', 'Y'][email_dialog.periodComboBox.currentIndex()],
                                          email_dialog.periodSpinBox.value(), self)
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
        self._recalculate_indices()

    def remove_email_task(self):
        self.filesTableWidget.removeRow(self.filesTableWidget.selectedIndexes()[0].row())
        self._recalculate_indices()

    def edit_email_task(self):
        email_dialog = EmailDialog(self)
        selected_index = self.filesTableWidget.selectedIndexes()[0].row()
        message = self.filesTableWidget.item(selected_index, 0).data
        assert isinstance(message, TimedEmailMessage)
        email_dialog.setWindowTitle(self.tr('Edit a task'))
        email_dialog.toLineEdit.setText(message['To'])
        email_dialog.subjectLineEdit.setText(message['Subject'])
        email_dialog.bodyPlainTextEdit.setPlainText(message.text)
        email_dialog.filePathLlineEdit.setText(message.attachment_path)
        email_dialog.periodSpinBox.setValue(message.time_count)
        email_dialog.periodComboBox.setCurrentIndex(['m', 'h', 'd', 'w', 'M', 'Y'].index(message.time_unit))

        def email_dialog_accepted():
            items = self._get_info_as_items(email_dialog)
            for i, item in enumerate(items):
                self.filesTableWidget.setItem(selected_index, i, item)

        email_dialog.accepted.connect(email_dialog_accepted)
        email_dialog.exec()
        self._recalculate_indices()

    def preview_email(self):
        if self.filesTableWidget.selectedIndexes():
            selected_index = self.filesTableWidget.selectedIndexes()[0].row()
            message = self.filesTableWidget.item(selected_index, 0).data
            assert isinstance(message, TimedEmailMessage)
            self.emailGroupBox.setEnabled(True)
            self.toLineEdit.setText(message['To'])
            self.subjectLineEdit.setText(message['Subject'])
            self.bodyPlainTextEdit.setPlainText(message.text)
            self.attachmentLineEdit.setText(message.attachment_path)
        else:
            self.emailGroupBox.setEnabled(False)
            self.toLineEdit.setText('')
            self.subjectLineEdit.setText('')
            self.bodyPlainTextEdit.setPlainText('')
            self.attachmentLineEdit.setText('')

    def send_email(self):
        selected_index = self.filesTableWidget.selectedIndexes()[0].row()
        message = self.filesTableWidget.item(selected_index, 0).data
        assert isinstance(message, TimedEmailMessage)
        Thread(target=partial(message.send, server=self.serverAddressLineEdit.text(),
                              port=self.serverPortSpinBox.value(), username=self.usernameLineEdit.text(),
                              password=self.passwordLineEdit.text(), tls=self.tlsCheckBox.isChecked())).start()
        self.sendPushButton.setEnabled(False)
        self.sendPushButton.setFont(ITALIC_FONT)
        self.statusbar.showMessage(self.tr('Sending a message...'), 3000)

    @pyqtSlot(TimedEmailMessage)
    def update_ui_after_send(self, message):
        assert isinstance(message, TimedEmailMessage)
        self.filesTableWidget.setItem(message.index, 3, DataQTableWidgetItem(str(message.last_sent)))
        self.filesTableWidget.setItem(message.index, 4, DataQTableWidgetItem(str(message.next_send)))
        self.sendPushButton.setFont(QFont())
        self.sendPushButton.setEnabled(True)
        self.statusbar.showMessage(self.tr('Message sent'), 3000)

    def open_tasks_file_selection_window(self):
        path = QFileDialog.getOpenFileName(self, self.tr('Choose a file'), filter=self.tr('PES task files (*.pes)'))[0]
        if path:
            self.tasksFileLineEdit.setText(path)


app = QApplication(sys.argv)
window = MainWindow()
sys.exit(app.exec())
