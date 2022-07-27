import socket

server_listening_port = 9000

sockfd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sockfd.bind(("", server_listening_port))
print("Listening on the port " + str(server_listening_port))

client_requests = []

def send_ports(client_a, client_b):
    global client_requests

    print(client_a)
    print(client_b)
    print("\n")

    sockfd.sendto(str(client_a[1][1]).encode("utf-8"), client_b[1])
    sockfd.sendto(str(client_b[1][1]).encode("utf-8"), client_a[1])


while True:
    data, addr = sockfd.recvfrom(32)

    sockfd.sendto(bytes("ack", "utf-8"), addr)
    
    found = False
    for c in client_requests:
        if c[0] == data:
            client_requests.remove(c)
            send_ports((data, addr), c)
            found = True
            break

    if not found: client_requests.append((data, addr))