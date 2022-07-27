import socket
import struct
import sys
import time
master = ("lbartolini.ddns.net", 9000)

#Create dgram udp socket
try:
    sockfd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    message = "Hello"
    sockfd.bind(('', 0))
    sockfd.sendto(message.encode("utf-8"), master)

except socket.error:
    print("Failed to create socket")
    sys.exit()

# #Receiving peer info from server
peer_data, addr = sockfd.recvfrom(1024)
print (peer_data)

print("trying to communicate with peer")
peer_ip = peer_data.decode("utf-8").split(":")[0]
peer_port = int(peer_data.decode("utf-8").split(":")[1])

peer = (peer_ip, peer_port)

while 1:
    message1 = input(str("You:>>"))
    message = message.encode("utf-8")
    sockfd.sendto(str(message).encode("utf-8"), peer)
    incoming_msg, sendaddr = sockfd.recvfrom(1024)
    incoming_msg = incoming_msg.decode("utf-8")
    print("ClientB:>>",incoming_msg)