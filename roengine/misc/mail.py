# -*- coding: UTF-8 -*-

import smtplib
import os
import zipfile

from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate


class Email(object):
    def __init__(self, init_msg=True, send_msg=False, from_addr="user@example.com", to_addrs=("user@example.com",),
                 body="", subject="Test Email", bodytype="plain", attachments=(), psw="l3tm31n!"):
        self.contents = {'From': from_addr, 'To': to_addrs, 'Body': body, 'BodyType': bodytype,
                         'Attachments': attachments, 'Password': psw, 'Subject': subject}
        self.MIME = MIMEMultipart()
        if init_msg:
            self.init_mime()
        if send_msg:
            self.send_and_quit()

    def __getitem__(self, item):
        return self.contents[item]

    def init_mime(self):
        self.MIME['Subject'] = self.contents['Subject']
        self.MIME['From'] = self.contents['From']
        self.MIME['Date'] = formatdate(localtime=True)
        self.MIME['To'] = COMMASPACE.join(self.contents['To'])

        self.MIME.attach(MIMEText(self.contents['Body'], self.contents['BodyType']))

        for f in self.contents['Attachments']:
            with open(f, "rb") as fp:
                part = MIMEApplication(fp.read(), Name=basename(f))
            part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
            self.MIME.attach(part)
        return self.MIME

    def send_and_quit(self, debug_lvl=1, host='smtp.gmail.com', port=465):
        server = smtplib.SMTP_SSL(host, port)
        server.set_debuglevel(debug_lvl)
        server.login(self.contents['From'], self.contents['Password'])
        server.sendmail(self.contents['From'], self.contents['To'], self.MIME.as_string())
        server.quit()
        return server

    def send_from_new(self, debug_lvl=1, host='smtp.gmail.com', port=465):
        new = MailServer(host, port, debug_lvl)
        new.start()
        new.send_email(self)
        return new

    def send_from(self, serv):
        serv.send_email(self)


class MailServer(object):
    def __init__(self, host='smtp.gmail.com', port=465, dbg=1, from_addr='user@example.com',
                 to_addrs=('user@example.com',), psw='l3tm31n!', start=False):
        self.addr = host, port
        self._server = None
        self.from_addr = from_addr
        self.to_addrs = to_addrs
        self.psw = psw
        self.debug_lvl = dbg
        if start:
            self.start()
            self.login(self.from_addr, self.to_addrs, self.psw)

    def start(self):
        self._server = smtplib.SMTP_SSL(*self.addr)
        self._server.set_debuglevel(self.debug_lvl)
        self._server.ehlo_or_helo_if_needed()

    def stop(self):
        self._server.quit()

    def send_email(self, mail):
        if self._server is None:
            self.start()
        self.raw_send(mail.MIME.as_string(), from_addr=mail['From'], to_addrs=mail['To'], psw=mail['Password'])

    def raw_send(self, txt, **kwargs):
        if kwargs:
            self.login(**kwargs)
        self._server.sendmail(self.from_addr, self.to_addrs, txt)

    def login(self, from_addr='user@example.com', to_addrs=('user@example.com',), psw='l3tm31n!'):
        self._server.login(from_addr, psw)
        self.from_addr = from_addr
        self.to_addrs = to_addrs
        self.psw = psw


def zip_file(dir, filename):
    """
    Add the contents of dir to zipfile.

    :param dir: str
    :param filename: str (the name of the zip file)
    :return: None
    """
    zp = zipfile.ZipFile(filename, "w")
    for i in os.walk(dir, followlinks=True):
        for fp in i[2]:
            path = os.path.join(i[0], fp)
            rel = os.path.relpath(path, dir)
            zp.write(path, rel)
    return zp


if __name__ == '__main__':
    import os
    FROM = 'ha.lol.no.u@gmail.com'
    PSW = 'PurpleAndBlack'
    TO = ['25sahilv@students.harker.org']

    serv = MailServer()
    mail = Email(from_addr=FROM, to_addrs=TO, psw=PSW, body=os.urandom(4096*8), subject='Sound of death',
                 attachments=('/Users/Grant/Downloads/terror.wav', ))
    mail.send_from(serv)
    serv.stop()
