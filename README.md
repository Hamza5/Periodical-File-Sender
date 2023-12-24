# Periodical File Sender (PFS)
#### (Formerly known as Periodical Email Sender - PES)
#### GUI-based tool to send emails with attachment periodically using an SMTP server

## Description

**Periodical File Sender** is a simple automation application that was designed
according to one client needs. This desktop application features an intuitive
user interface composed of two tabs: **Settings** and **Sending options**.

### Settings

This is the first view that appears in the first run of the application. It
shows the permanent settings that should be set in order to make the
application work. It is made of several sections:

#### Mail server settings

In this section the user has to enter the hostname, the port, and the SSL/TLS
status of the SMTP server that will be used for sending the emails. This
information can be obtained from the email service provider.

#### Login

The next section holds the username and the password that will be used for
authentication. This information should also be provided by the email service
provider.

#### Sender information

This section specifies the name and the email address that will be displayed
to the receiver.

_Although the user can put anything here, most SMTP servers
will not allow you to put anything other than what represents your real
identity on the email service provider. Even if a service provider allows
you to misrepresent the identity, the email will most likely ends up in the
spam folder of the receiver because it will be flagged as a non-legitimate
email._

#### Tasks file

The last section allows the selection of the tasks file where the periodical
sending tasks will be saved.

Finally, these settings must be saved using the <kbd>Save</kbd> button at the
bottom. This will instantly generate a `settings.ini` file in the current
working directory and allows the user to use the **Sending options** tab.
