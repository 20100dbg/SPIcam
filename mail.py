import os
import smtplib
import config
from email.message import EmailMessage
from datetime import datetime

def sendmail(startDetect = True):
	gdh = datetime.now()
	dirImg = "images/"

	msg = EmailMessage()
	msg['To'] = config.CONF['mail_to']
	msg['From'] = config.CONF['mail_from']
	msg['Subject'] = config.CONF['mail_subject']
	
	if startDetect:
		msg.set_content("Alerte intrusion " + str(gdh))
		for filename in os.listdir(dirImg):
		    pathPJ = os.path.join(dirImg, filename)

		    with open(pathPJ, 'rb') as fp:
		        msg.add_attachment(fp.read(), maintype='application', subtype='octet-stream', filename=filename)
	else:
		msg.set_content("Fin d'intrusion " + str(gdh))

	# Send the message via our own SMTP server.
	s = smtplib.SMTP('localhost',25)
	s.login(config.CONF['smtp_login'], config.CONF['smtp_password'])

	s.send_message(msg)
	s.quit()
