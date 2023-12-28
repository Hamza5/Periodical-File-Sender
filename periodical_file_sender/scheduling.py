import email.message
import mimetypes
import os.path
import sys
from datetime import datetime, timedelta
from smtplib import SMTP_SSL, SMTP
from threading import Event, Thread, Lock
from time import sleep

MONITORING_FREQUENCY = 1


class TimedEmailMessage:
    # Note: Subclassing email.message.EmailMessage generates an exception, so it is not possible.

    def set_last_sent(self, last_sent):
        self.lock.acquire()
        self._last_sent = last_sent
        self.lock.release()

    def get_last_sent(self):
        self.lock.acquire()
        last_sent = datetime.fromtimestamp(self._last_sent.timestamp()) if self._last_sent else None
        self.lock.release()
        return last_sent

    def set_next_send(self, next_send):
        self.lock.acquire()
        self._next_send = next_send
        self.lock.release()

    def get_next_send(self):
        self.lock.acquire()
        next_send = datetime.fromtimestamp(self._next_send.timestamp()) if self._next_send else None
        self.lock.release()
        return next_send

    last_sent = property(get_last_sent, set_last_sent)
    next_send = property(get_next_send, set_next_send)

    def __init__(self, sender, receiver, title, text, attachment_filepath, time_unit, time_count, parent_gui=None):
        assert isinstance(sender, str) and '@' in sender
        assert isinstance(receiver, str) and '@' in receiver
        assert isinstance(title, str)
        assert isinstance(text, str)
        assert attachment_filepath is None or isinstance(attachment_filepath, str)
        assert time_unit in 'mhdwMY'
        assert isinstance(time_count, int)
        self.message = email.message.EmailMessage()
        self['From'] = sender
        self['To'] = receiver
        self['Subject'] = title
        self.text = text
        self.attachment_path = attachment_filepath
        self.time_unit = time_unit
        self.time_count = time_count
        self.lock = Lock()
        self._last_sent = None
        self._next_send = None
        self.parent_gui = parent_gui
        self.index = None
        self.calculate_next_sending_time()

    def __setitem__(self, key, value):
        self.message[key] = value

    def __getitem__(self, item):
        return self.message[item]

    def send(self, server, port, username, password, tls=True):
        assert isinstance(server, str)
        assert isinstance(port, int)
        assert isinstance(username, str)
        assert isinstance(password, str)
        if self.parent_gui is not None:
            self.parent_gui.email_before_send.emit(self)
        self.message.clear_content()
        self.message.set_content(self.text)
        if self.attachment_path:
            ctype, encoding = mimetypes.guess_type(self.attachment_path)
            if ctype is None:
                ctype = 'application/octet-stream'
            maintype, subtype = ctype.split('/')
            with open(self.attachment_path, 'rb') as attachment_file:
                self.message.add_attachment(attachment_file.read(), maintype=maintype, subtype=subtype,
                                            filename=os.path.basename(self.attachment_path))
        if tls:
            smtp_server = SMTP_SSL(server, port)
        else:
            smtp_server = SMTP(server, port)
        smtp_server.login(username, password)
        smtp_server.send_message(self.message)
        smtp_server.quit()
        self.last_sent = datetime.now().replace(microsecond=0)
        self.calculate_next_sending_time()
        if self.parent_gui is not None:
            self.parent_gui.email_after_send.emit(self)

    def calculate_next_sending_time(self):
        was_sent = bool(self.last_sent)
        if not was_sent:
            self.last_sent = datetime.now()
        if self.time_unit == 'M':
            self.next_send = (self.last_sent + timedelta(days=31 * self.time_count)) \
                .replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif self.time_unit == 'Y':
            self.next_send = (self.last_sent + timedelta(days=366 * self.time_count)) \
                .replace(day=1, month=1, hour=0, minute=0, second=0, microsecond=0)
        elif self.time_unit == 'w':
            self.next_send = (self.last_sent + timedelta(weeks=self.time_count)).replace(microsecond=0)
        elif self.time_unit == 'd':
            self.next_send = (self.last_sent + timedelta(days=self.time_count)).replace(microsecond=0)
        elif self.time_unit == 'h':
            self.next_send = (self.last_sent + timedelta(hours=self.time_count)).replace(microsecond=0)
        elif self.time_unit == 'm':
            self.next_send = (self.last_sent + timedelta(minutes=self.time_count)).replace(microsecond=0)
        if not was_sent:
            self.last_sent = None


class SendingTimeMonitor(Thread):

    def __init__(self, server_address, server_port, username, password, tls, parent_gui):
        super().__init__()
        self.stopped = Event()
        self.server_address = server_address
        self.server_port = server_port
        self.username = username
        self.password = password
        self.tls = tls
        self.gui = parent_gui

    def get_ready_messages(self):
        ready_messages = []
        now = datetime.now()
        for message in self.gui.get_messages():
            assert isinstance(message, TimedEmailMessage)
            if message.next_send <= now:
                ready_messages.append(message)
        return ready_messages

    def stop(self):
        self.stopped.set()

    def run(self):
        try:
            while not self.stopped.is_set():
                sleep(MONITORING_FREQUENCY)
                for msg in self.get_ready_messages():
                    assert isinstance(msg, TimedEmailMessage)
                    msg.send(self.server_address, self.server_port, self.username, self.password, self.tls)
                    msg.calculate_next_sending_time()
        except Exception:
            sys.excepthook(*sys.exc_info())
