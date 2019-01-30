from collections import Iterable
from datetime import datetime
from threading import Event, Lock
from time import sleep

from email_message import TimedEmailMessage
from fixed_thread import Thread

MONITORING_FREQUENCY = 1


class SendingTimeMonitor(Thread):

    def __init__(self, server_address, server_port, username, password, tls):
        super().__init__()
        self.stopped = Event()
        self.msgs = []
        self.server_address = server_address
        self.server_port = server_port
        self.username = username
        self.password = password
        self.tls = tls
        self.lock = Lock()

    def get_ready_messages(self):
        ready_messages = []
        now = datetime.now()
        self.lock.acquire()
        for message in self.msgs:
            assert isinstance(message, TimedEmailMessage)
            if message.next_send <= now:
                ready_messages.append(message)
        self.lock.release()
        return ready_messages

    def set_messages(self, messages):
        assert isinstance(messages, Iterable) and all(isinstance(x, TimedEmailMessage) for x in messages)
        self.lock.acquire()
        self.msgs = messages
        self.lock.release()

    def get_messages(self):
        self.lock.acquire()
        messages = self.msgs.copy()
        self.lock.release()
        return messages

    messages = property(get_messages, set_messages)

    def stop(self):
        self.stopped.set()

    def run(self):
        while not self.stopped.is_set():
            sleep(MONITORING_FREQUENCY)
            for msg in self.get_ready_messages():
                assert isinstance(msg, TimedEmailMessage)
                msg.send(self.server_address, self.server_port, self.username, self.password, self.tls)
                msg.calculate_next_sending_time()
