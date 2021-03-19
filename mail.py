import os
import smtplib
import config
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from datetime import datetime

def sendmail(startDetect = True):
	gdh = datetime.now().strftime("%Y%m%d_%H%M") 

	dirImg = "images/"

	#msg = EmailMessage()
	msg = MIMEMultipart('related')
	msg['To'] = config.CONF['mail_to']
	msg['From'] = config.CONF['mail_from']
	msg['Subject'] = "Alerte intrusion" if startDetect else "Fin alerte intrusion"
	
	if startDetect:
		html = f"""<p>Alerte intrusion {gdh}<br>"""


		for filename in os.listdir(dirImg):
			pathPJ = os.path.join(dirImg, filename)

			with open(pathPJ, 'rb') as fp:
				#msg.add_attachment(fp.read(), maintype='application', subtype='octet-stream', filename=filename)
				f, e = os.path.splitext(filename)
				html += f"""<img src="cid:{f}"><br>"""
				msgImg = MIMEImage(fp.read(), e)
				msgImg.add_header('Content-ID', '<'+ f +'>')
				msgImg.add_header('Content-Disposition', 'inline', filename=filename)
				msg.attach(msgImg)

		html += f"""</p>"""
	else:
		html = f"""<p>Fin alerte intrusion {gdh}<br></p>"""

	msg.attach(MIMEText(html, 'html'))

	# Send the message via our own SMTP server.
	s = smtplib.SMTP('localhost',25)

	if config.CONF['use_smtp_login']:
		s.login(config.CONF['smtp_login'], config.CONF['smtp_password'])

	s.sendmail(msg['From'], msg['To'], msg.as_string())
	#s.send_message(msg)
	s.quit()
