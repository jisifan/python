import socket


ip = "127.0.0.1"
port = 5000
s = socket.socket()
s.connect((ip,port))
message = input("->")
while message != 'q':
	s.send(str.encode(message))
	# print("sent to Server:" + str(message))
	data = s.recv(1024)
	print("receive from Server:" + bytes.decode(data))
	message = input("->")
s.close()
# add a comment for test