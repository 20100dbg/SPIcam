import socket
import os

run = True
i = 0
# start serveur command
# start motion.py

os.system("sub1.py")

#mise en écoute
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('',5555))
s.listen()


while run:
	
    con, addr = s.accept()
    
    message = socket.recv(1024)
    print(f"Received request: {message}")

    sleep(1)

	run = False
	con.close()

s.close()
