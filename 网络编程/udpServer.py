import socket

port = 5000

s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
s.bind(("",port))

print("Server Started")

while True:
	data, addr = s.recvfrom(1024)
	if(bytes.decode(data) == 'q'):
		break
	print("message for:" + str(addr))
	print("from connected user:" + bytes.decode(data))
	data = bytes.decode(data).upper()
	s.sendto(str.encode(data),addr)
s.close()