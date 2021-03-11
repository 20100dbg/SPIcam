import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import config

flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
creds = flow.run_local_server(port=0)
service = build('gmail', 'v1', credentials=creds)

# Call the Gmail API
results = service.users().labels().list(userId='me').execute()

message = MIMEMultipart("alternative")
message["subject"] = "Alerte intrusion"
message["from"] = "alert@bcc.com"
message["to"] = config.CONF['email']

html = """\
	<html><body><p>
       <a href="http://www.realpython.com">Real Python</a> 
    </p></body></html>
"""

# Add HTML/plain-text parts to MIMEMultipart message
# The email client will try to render the last part first
message.attach(MIMEText(html, "html"))

content_type = 'application/octet-stream'
main_type, sub_type = content_type.split('/', 1)

fp = open(file, 'rb')
msg = MIMEBase(main_type, sub_type)
msg.set_payload(fp.read())
fp.close()

filename = os.path.basename(file)
msg.add_header('Content-Disposition', 'attachment', filename=filename)
message.attach(msg)

try:
	message = (service.users().messages().send(userId="me", body={'raw': base64.urlsafe_b64encode(message.as_string())}).execute())
	print 'Message Id: %s' % message['id']
	return message
except errors.HttpError, error:
	print 'An error occurred: %s' % error