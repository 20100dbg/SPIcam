import socket


#####client
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("127.0.0.1", 5555))

s.send(b"salut c'est sub1")

s.close()