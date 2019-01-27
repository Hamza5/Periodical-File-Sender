import json
import sys
from configparser import ConfigParser
from datetime import datetime
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

    SETTINGS_FILE_PATH = 'settings.ini'

    email_sent = pyqtSignal(TimedEmailMessage)
    tasks_changed = pyqtSignal()
    settings_changed = pyqtSignal()

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
        self.settingsButtonBox.clicked.connect(
            lambda b: self.save_settings()
            if self.settingsButtonBox.standardButton(b) == self.settingsButtonBox.Save
            else self.load_settings()
        )
        self.tasks_changed.connect(self._recalculate_indices)
        self.tasks_changed.connect(self.save_tasks)
        self.settings_changed.connect(self.load_tasks)
        self.send_monitor = SendingTimeMonitor(self.serverAddressLineEdit.text(), self.serverPortSpinBox.value(),
                                               self.usernameLineEdit.text(), self.passwordLineEdit.text(),
                                               self.tlsCheckBox.isChecked())
        self.load_settings()
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
            self.tasks_changed.emit()

        email_dialog.accepted.connect(email_dialog_accepted)
        email_dialog.exec()

    def remove_email_task(self):
        self.filesTableWidget.removeRow(self.filesTableWidget.selectedIndexes()[0].row())
        self.tasks_changed.emit()

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
            self.tasks_changed.emit()

        email_dialog.accepted.connect(email_dialog_accepted)
        email_dialog.exec()

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
        self.tasks_changed.emit()

    def open_tasks_file_selection_window(self):
        path = QFileDialog.getOpenFileName(self, self.tr('Choose a file'), filter=self.tr('Task files (*.json)'))[0]
        if path:
            self.tasksFileLineEdit.setText(path)

    def load_settings(self):
        try:
            with open(self.SETTINGS_FILE_PATH) as settings_file:
                settings_parser = ConfigParser()
                settings_parser.read_file(settings_file)
                self.serverAddressLineEdit.setText(settings_parser.get('Server', 'Address', fallback=''))
                self.serverPortSpinBox.setValue(settings_parser.getint('Server', 'Port', fallback=465))
                self.usernameLineEdit.setText(settings_parser.get('Server', 'Username', fallback=''))
                self.passwordLineEdit.setText(settings_parser.get('Server', 'Password', fallback=''))
                self.senderNameLineEdit.setText(settings_parser.get('Sender', 'Name', fallback=''))
                self.senderEmailLineEdit.setText(settings_parser.get('Sender', 'EmailAddress', fallback=''))
                self.tasksFileLineEdit.setText(settings_parser.get('Tasks', 'FilePath', fallback='send_tasks.json'))
                self.settings_changed.emit()
        except FileNotFoundError:
            pass

    def save_settings(self):
        settings_parser = ConfigParser()
        settings_parser['Server'] = {'Address': self.serverAddressLineEdit.text(),
                                     'Port': self.serverPortSpinBox.value(),
                                     'Username': self.usernameLineEdit.text(),
                                     'Password': self.passwordLineEdit.text()}
        settings_parser['Sender'] = {'Name': self.senderNameLineEdit.text(),
                                     'EmailAddress': self.senderEmailLineEdit.text()}
        settings_parser['Tasks'] = {'FilePath': self.tasksFileLineEdit.text()}
        with open(self.SETTINGS_FILE_PATH, 'w') as settings_file:
            settings_parser.write(settings_file)
        self.settings_changed.emit()

    def load_tasks(self):
        path = self.tasksFileLineEdit.text()
        if path:
            try:
                with open(path) as tasks_file:
                    tasks_json = json.load(tasks_file)
                    assert isinstance(tasks_json, list)
                    self.filesTableWidget.clearContents()
                    self.filesTableWidget.setRowCount(len(tasks_json))
                    for i, task_json in enumerate(tasks_json):
                        to = task_json['To']
                        subject = task_json['Subject']
                        text = task_json['Text']
                        attachment = task_json['Attachment']
                        time_unit = task_json['Time unit']
                        time_count = task_json['Time count']
                        last_run = task_json['Last run']
                        next_run = task_json['Next run']
                        message = TimedEmailMessage(to, self.senderEmailLineEdit.text(), subject, text, attachment,
                                                    time_unit, time_count, self)
                        message.index = i
                        message.last_sent = datetime.fromtimestamp(last_run) if last_run else None
                        message.next_send = datetime.fromtimestamp(next_run)
                        for j, item in enumerate(
                                [DataQTableWidgetItem(subject, message), DataQTableWidgetItem(to),
                                 DataQTableWidgetItem(self.tr('Every') + ' ' + str(time_count) + ' ' +
                                                      {'m': 'Minutes', 'h': 'Hours', 'd': 'Days',
                                                       'w': 'Weeks', 'M': 'Months', 'Y': 'Years'}[time_unit]),
                                 DataQTableWidgetItem(str(message.last_sent)) if last_run else DataQTableWidgetItem(),
                                 DataQTableWidgetItem(str(message.next_send))]
                        ):
                            self.filesTableWidget.setItem(i, j, item)
            except FileNotFoundError:
                pass

    def save_tasks(self):
        tasks_json = []
        for i in range(self.filesTableWidget.rowCount()):
            message = self.filesTableWidget.item(i, 0).data
            assert isinstance(message, TimedEmailMessage)
            tasks_json.append({'To': message['To'], 'Subject': message['Subject'], 'Text': message.text,
                               'Attachment': message.attachment_path, 'Time unit': message.time_unit,
                               'Time count': message.time_count, 'Next run': int(message.next_send.timestamp()),
                               'Last run': message.last_sent.timestamp() if message.last_sent else 0})
        try:
            with open(self.tasksFileLineEdit.text(), 'w') as tasks_file:
                json.dump(tasks_json, tasks_file)
        except OSError:
            pass


app = QApplication(sys.argv)
window = MainWindow()
sys.exit(app.exec())
