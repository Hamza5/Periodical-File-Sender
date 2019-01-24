from datetime import datetime
from threading import Thread, Event
from time import sleep

from email_message import TimedEmailMessage

MONITORING_FREQUENCY = 1


class SendingTimeMonitor(Thread):

    def __init__(self, server_address, server_port, username, password, tls):
        super().__init__()
        self.stopped = Event()
        self.messages = []
        self.server_address = server_address
        self.server_port = server_port
        self.username = username
        self.password = password
        self.tls = tls

    def get_ready_messages(self):
        ready_messages = []
        now = datetime.now()
        for message in self.messages:
            assert isinstance(message, TimedEmailMessage)
            if message.next_send <= now:
                ready_messages.append(message)
        return ready_messages

    def stop(self):
        self.stopped.set()

    def run(self):
        while not self.stopped.is_set():
            sleep(MONITORING_FREQUENCY)
            for msg in self.get_ready_messages():
                assert isinstance(msg, TimedEmailMessage)
                print('Sending...')
                msg.send(self.server_address, self.server_port, self.username, self.password, self.tls)
                print('Email "{}" sent on {}'.format(msg['Subject'], msg.last_sent))
                msg.calculate_next_sending_time()
        # TODO update the GUI
