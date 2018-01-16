import socket

ip = "127.0.0.1"
port = 5000
s = socket.socket()
s.bind(("127.0.0.1",port))
s.listen(1)
c, addr = s.accept()
print("Connection from:"+str(addr))
while True:
	data = c.recv(1024)
	if not data:
		break
	print("from connected user:" + bytes.decode(data))
	message = input("->")
	c.send(str.encode(message))
	# print("sent to Client:" + str(message))
c.close()