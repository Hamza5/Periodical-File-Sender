import sys
from datetime import datetime
from threading import Event, Thread
from time import sleep

from email_message import TimedEmailMessage

MONITORING_FREQUENCY = 1


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
