import socket

known_port = 50002

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', 9000))

while True:
    clients = []

    while True:
        data, address = sock.recvfrom(128)

        print('connection from: {}'.format(address))
        clients.append(address)

        sock.sendto(b'ready', address)

        if len(clients) == 2:
            print('got 2 clients, sending details to each')
            break

    c1 = clients.pop()
    c1_addr, c1_port = c1
    c2 = clients.pop()
    c2_addr, c2_port = c2

    sock.sendto('{} {} {}'.format(c1_addr, c1_port, known_port).encode(), c2)
    sock.sendto('{} {} {}'.format(c2_addr, c2_port, known_port).encode(), c1)

'''import socket

server_listening_port = 9000

sockfd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sockfd.bind(("", server_listening_port))
print("Listening on the port " + str(server_listening_port))

client_requests = []

def send_ports(client_a, client_b):
    global client_requests

    sockfd.sendto(str(client_a[1][1]).encode("utf-8"), client_b[1])
    sockfd.sendto(str(client_b[1][1]).encode("utf-8"), client_a[1])


while True:
    data, addr = sockfd.recvfrom(32)
    
    found = False
    for c in client_requests:
        if c[0] == data:
            client_requests.remove(c)
            send_ports((data, addr), c)
            found = True
            break

    if not found: client_requests.append((data, addr))'''