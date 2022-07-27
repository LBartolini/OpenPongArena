import socket

server_listening_port = 9000

sockfd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sockfd.bind(("", server_listening_port))
print("Listening on the port " + str(server_listening_port))

client_requests = []

while True:
    data, addr = sockfd.recvfrom(32)
    client_requests.append(addr)
    print("Connection from: " + str(addr))

    if len(client_requests) == 2:
        client_a_ip = client_requests[0][0]
        client_a_port = client_requests[0][1]
        client_b_ip = client_requests[1][0]
        client_b_port = client_requests[1][1]

        message = ": "

        sockfd.sendto(str(client_a_ip).encode("utf-8") + message.encode("utf-8") + str(client_a_port).encode("utf-8"), client_requests[1])
        sockfd.sendto(str(client_b_ip).encode("utf-8") + message.encode("utf-8") + str(client_b_port).encode("utf-8"), client_requests[0])

        client_requests = []