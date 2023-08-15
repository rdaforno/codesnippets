#!/usr/bin/env python

"""
Mail to http forwarder

Checks for mails and forwards them via an HTTP GET request to a server.
On the server side, the data can be received and processed with a simple php script:

<?php
if (isset($_GET['id'])) {
    $id = $_GET['id'];
    $from = base64_decode($_GET['from']);
    $subject = base64_decode($_GET['subject']);
    $content = base64_decode($_GET['content']);
    echo "$id";
    //TODO: process data
}
?>

All that is left to do is to periodically run this script.
"""

import os
import imaplib
import email
import base64
import urllib.request


# mail server settings
username = "username"
password = "password"
imapserver = "imap.mymailserver.com"
subjectfilter = None
senderfilter = None
httpserver = "https://myhttpserver.com/myparserscript.php"
statusfile = "status"


class Mail2Http:
    
    def __init__(self, lastsent = 0, subjectfilter = None, senderfilter = None):
        self.lastsent = lastsent
        self.subjectfilter = subjectfilter
        self.senderfilter = senderfilter
        self.imap = None
        self.msgcnt = 0
        self.messages = []
   
    def connect(self, server, username, passwd):
        self.imap = imaplib.IMAP4_SSL(imapserver)
        self.imap.login(username, passwd)
        status, msg = self.imap.select("INBOX")
        self.msgcnt = int(msg[0])
        print("connected")
        print("mailbox contains %d message(s)" % self.msgcnt)
    
    def disconnect(self):
        if not self.imap:
            return
        self.imap.close()
        self.imap.logout()
        print("disconnected")
    
    def clear(self):
        self.message.clear()
    
    def printMessages(self):
        for msg in self.messages:
            print("Subject:", msg['subject'])
            print("From:   ", msg['from'])
            print("Content:", msg['content'])
            print("---")
    
    def fetch(self, num = 0):
        if not self.imap:
            return
        if self.lastsent >= self.msgcnt:
            print("no new messages")
            return
        if num == 0 or num > self.msgcnt:
            num = self.msgcnt
        for i in range(self.msgcnt, self.msgcnt - num, -1):
            try:
                msg = self.fetchMail(i)
                if self.subjectfilter and self.subjectfilter not in msg['subject']:
                    continue
                if self.senderfilter and self.senderfilter not in msg['from']:
                    continue
                self.messages.append(msg)
            except:
                print("failed to fetch message %d" % i)
    
    def fetchMail(self, id):
        if not self.imap:
            return None
        # email fetching routing is based on https://www.thepythoncode.com/article/reading-emails-in-python
        message = { 'id': id, 'subject': '', 'from': '', 'content': '' }
        res, msg = self.imap.fetch(str(id), "(RFC822)")
        for response in msg:
            if isinstance(response, tuple):
                msg = email.message_from_bytes(response[1])
                subject, enc = email.header.decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(enc)
                sender, enc = email.header.decode_header(msg.get("From"))[0]
                if isinstance(sender, bytes):
                    sender = sender.decode(enc)
                message['subject'] += subject.strip()
                message['from'] += sender.strip()
                if msg.is_multipart():
                    for part in msg.walk():
                        ctype = part.get_content_type()
                        if ctype == "text/plain":
                            body = part.get_payload(decode=True).decode().strip()
                            message['content'] += body
                else:
                    ctype = msg.get_content_type()
                    if ctype == "text/plain":
                        body = msg.get_payload(decode=True).decode().strip()
                        message['content'] += body
        return message

    def encode(self, str):
        return base64.b64encode(str.encode('ascii')).decode('ascii')
    
    def decode(self, str):
        return base64.b64decode(str.encode('ascii')).decode('ascii')

    def forward(self, serverurl):
        for msg in self.messages:
            if msg['id'] <= self.lastsent:
                continue
            url = "%s?id=%s&from=%s&subject=%s&content=%s" % (serverurl, msg['id'], self.encode(msg['from']), self.encode(msg['subject']), self.encode(msg['content']))
            response = urllib.request.urlopen(url).read().decode()
            print(response)
            if str(msg['id']) not in response:
                print("failed to forward message %d: %s" % (msg['id'], response))
                break
            self.lastsent = msg['id']
            print("message with id %d forwarded" % msg['id'])
        return self.lastsent



if __name__ == "__main__":

    lastforwardedmsg = 0
    if os.path.isfile(statusfile):
        with open(statusfile, 'r') as f:
            lastforwardedmsg = int(f.read().strip() or 0)
            print("last message id was %d" % lastforwardedmsg)

    mailforwarder = Mail2Http(lastforwardedmsg, subjectfilter, senderfilter)
    mailforwarder.connect(imapserver, username, password)
    mailforwarder.fetch()
    lastforwardedmsg = mailforwarder.forward(httpserver)
    mailforwarder.disconnect()

    with open(statusfile, 'w') as f:
        f.write(str(lastforwardedmsg))
