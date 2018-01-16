import socket

host = "127.0.0.1"
port = 5000

server = (host,port)

s= socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

s.bind(("127.0.0.1",5231))
message = input("->")

while True:
	if message == "q":
		break
	s.sendto(str.encode(message),server)
	data, addr = s.recvfrom(1024)
	print("Receive from Server:" + bytes.decode(data))
	message = input("->")
s.close()