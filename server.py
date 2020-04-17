import socket
import sys
import threading
import time

RECV_LENGTH = 4096


def clean_clients(a):
    for i in range(len(a) - 1, -1, -1):
        if a[i] is None:
            a.pop(i)
    printerr("Clients cleaned.")


def client_index(s):
    for i in range(len(clients)):
        if clients[i] is not None and clients[i][0] == s:
            return i


def printerr(text):
    print(text, file=sys.stderr)


def return_clients(a):
    out = ""
    for i in range(len(a)):
        if a[i] is not None:
            out += str(i) + " : " + str(a[i][1]) + " - " + str(a[i][0].getpeername())
        else:
            out += str(i) + " : None"
    return out


def print_clients(a):
    printerr("Clients :")
    for i in range(len(a)):
        if a[i] is not None:
            printerr(str(i) + " : " + str(a[i][1]) + " - " + str(a[i][0].getpeername()))
        else:
            printerr(str(i) + " : None")


def send_string(con, msg):
    con.sendall(msg.encode("ascii"))


def send_to_tag(msg, l_tag):
    for i in range(len(clients)):
        if clients[i] is not None and clients[i][1] == l_tag:
            send_string(clients[i][0], msg)


def send_to_first_tag(msg, l_tag):
    for i in range(len(clients)):
        if clients[i] is not None and clients[i][1] == l_tag:
            send_string(clients[i][0], msg)
            return


def client_tag(con):
    for i in range(len(clients)):
        if clients[i] is not None and clients[i][0] == con:
            return clients[i][1]


def assign_type(con):
    if client_index(con) % 2 == 0:
        return "CARS"
    else:
        return "DOGS"


def hello(con):
    client_type = assign_type(con)
    send_string(con, client_type)
    clients[client_index(con)][1] = client_type


def ping(con):
    send_string(con, "PONG")


def img(data):
    img_tag = data.split(",")[1]
    img_data = data.split(",")[2]
    send_to_tag(img_data, img_tag)


def stop(con):
    send_string(con, "ACK")


def connection_life(con, client_addr):
    tmp_data = ""
    try:
        print('connection from', client_addr)

        # Receive the data in small chunks and retransmit it
        while True:
            data = con.recv(RECV_LENGTH)
            if data:
                data_str = data.decode("ascii")
                printerr("received " + data_str + " from client " + str(client_index(con)))
                if data_str == "clean":
                    clean_clients(clients)
                    print_clients(clients)
                elif data_str == "list":
                    send_string(con, return_clients(clients))
                elif data_str == "tag":
                    send_string(con, client_tag(con))
                elif str.startswith(data_str, "HELLO"):
                    hello(con)
                elif str.startswith(data_str, "PING"):
                    ping(con)
                elif str.startswith(data_str, "STOP"):
                    stop(con)
                elif str.startswith(data_str, "IMG"):
                    img(data_str)
                else:
                    tmp_data += data_str
                    # Bricolage : ne fonctionne pas si la taille du paquet est un multiple de RECV_LENGTH
                    if len(data_str) != RECV_LENGTH:
                        # Remplacer ici par le comportement standard
                        print('sending data back to the client')
                        send_string(con, tmp_data)
                        tmp_data = ""
            else:
                print('closing connection with', client_addr[0])
                index = client_index(con)
                clients[index] = None
                break

    finally:
        print_clients(clients)
        con.close()


clients = []
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', 43000)
printerr("starting up on " + server_address[0] + " port " + str(server_address[1]))
sock.bind(server_address)
sock.listen(1)

while True:
    print('Waiting for a connection')
    connection, client_address = sock.accept()
    t = threading.Thread(target=connection_life, args=(connection, client_address))
    tag = "NOTAG"
    endpoint = (connection, tag)
    clients.append(list(endpoint))
    t.start()
    time.sleep(0.2)
    print_clients(clients)
    send_string(connection, tag)
