import os.path
import mimetypes
from smtplib import SMTP_SSL, SMTP
from email.message import EmailMessage


def make_email_message(sender, receiver, title, text, attachment_filepath=None):
    assert isinstance(sender, str) and '@' in sender
    assert isinstance(receiver, str) and '@' in receiver
    assert isinstance(title, str)
    assert isinstance(text, str)
    message = EmailMessage()
    message['From'] = sender
    message['To'] = receiver
    message['Subject'] = title
    message.set_content(text)
    if attachment_filepath is not None:
        ctype, encoding = mimetypes.guess_type(attachment_filepath)
        if ctype is None:
            ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/')
        with open(attachment_filepath, 'rb') as attachment_file:
            message.add_attachment(attachment_file.read(), maintype=maintype, subtype=subtype,
                                   filename=os.path.basename(attachment_filepath))
    return message


def send_email_message(message, server, port, username, password, tls=True):
    assert isinstance(message, EmailMessage)
    assert isinstance(server, str)
    assert isinstance(port, int)
    assert isinstance(username, str)
    assert isinstance(password, str)
    if tls:
        smtp_server = SMTP_SSL(server, port)
    else:
        smtp_server = SMTP(server, port)
    smtp_server.login(username, password)
    smtp_server.send_message(message)
    smtp_server.quit()
