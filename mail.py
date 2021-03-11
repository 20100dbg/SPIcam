import os
import smtplib
from email.message import EmailMessage

gdh = ""
pathPJ = "images/"

msg = EmailMessage()
msg.set_content(f"""
	Alerte intrusion !
	GDH : {gdh}
	""")

msg['Subject'] = f'Alerte intrusion'
msg['From'] = "alert@bcc.com"
msg['To'] = "vincent.marie@protonmail.com"

for filename in os.listdir(pathPJ):
    path = os.path.join(pathPJ, filename)

    with open(path, 'rb') as fp:
        msg.add_attachment(fp.read(), maintype='application', subtype='octet-stream', filename=filename)


# Send the message via our own SMTP server.
s = smtplib.SMTP('localhost',25)
s.login('alert@mail.spicam','vbion,cvern,ty')

s.send_message(msg)
s.quit()
