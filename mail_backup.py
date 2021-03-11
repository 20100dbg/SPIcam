from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
import config

flow = InstalledAppFlow.from_client_secrets_file('credentials.json', ['https://www.googleapis.com/auth/gmail.compose'])
creds = flow.run_local_server(port=0)
service = build('gmail', 'v1', credentials=creds)

# Call the Gmail API
#results = service.users().labels().list(userId='me').execute()

message = MIMEMultipart()
message["to"] = config.CONF['email']
message["from"] = "alert@bcc.com"
message["subject"] = "Alerte intrusion"

html = """\
	<html><body><p>
       <a href="http://www.internetshouldbeillegal.com">yo</a> 
    </p></body></html>
"""

message.attach(MIMEText(html, "html"))
file = "image.jpg";

fp = open(file, 'rb')
msg = MIMEBase('application', 'octet-stream')
msg.set_payload(fp.read())
fp.close()

msg.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file))
message.attach(msg)
body = {'raw': base64.urlsafe_b64encode(message.as_string())}

try:
	print(body)
	print(config.CONF['email'])

	message = (service.users().messages().send(userId=config.CONF['email'], body=body).execute())
	print('Message Id: %s' % message['id'])

except:
	print('An error occurred')