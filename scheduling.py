from datetime import datetime, timedelta
from threading import Thread, Event
from time import sleep

from email_class import EmailMessage

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
            assert isinstance(message, EmailMessage)
            if message.next_send <= now:
                ready_messages.append(message)
        return ready_messages

    def stop(self):
        self.stopped.set()

    def run(self):
        while not self.stopped.is_set():
            sleep(MONITORING_FREQUENCY)
            for msg in self.get_ready_messages():
                assert isinstance(msg, EmailMessage)
                print('Sending...')
                msg.send(self.server_address, self.server_port, self.username, self.password, self.tls)
                print('Email "{}" sent on {}'.format(msg['Subject'], msg.last_sent))
                self.set_next_send(msg)
        # TODO update the GUI

    @staticmethod
    def set_next_send(msg):
        was_sent = bool(msg.last_sent)
        if not was_sent:
            msg.last_sent = datetime.now()
        if msg.time_unit == 'M':
            msg.next_send = (msg.last_sent + timedelta(days=31 * msg.time_count)) \
                .replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif msg.time_unit == 'Y':
            msg.next_send = (msg.last_sent + timedelta(days=366 * msg.time_count)) \
                .replace(day=1, month=1, hour=0, minute=0, second=0, microsecond=0)
        elif msg.time_unit == 'w':
            msg.next_send = (msg.last_sent + timedelta(weeks=msg.time_count)).replace(microsecond=0)
        elif msg.time_unit == 'd':
            msg.next_send = (msg.last_sent + timedelta(days=msg.time_count)).replace(microsecond=0)
        elif msg.time_unit == 'h':
            msg.next_send = (msg.last_sent + timedelta(hours=msg.time_count)).replace(microsecond=0)
        elif msg.time_unit == 'm':
            msg.next_send = (msg.last_sent + timedelta(minutes=msg.time_count)).replace(microsecond=0)
        if not was_sent:
            msg.last_sent = None
