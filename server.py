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


def printerr(text):
    print(text, file=sys.stderr)


def return_clients(a):
    out = ""
    for i in range(len(a)):
        out += str(i) + " : " + str(a[i])
    return out


def print_clients(a):
    printerr("Clients :")
    for i in range(len(a)):
        printerr(str(i) + " : " + str(a[i]))


def send_string(con, str):
    con.sendall(str.encode("ascii"))


def connection_life(con, client_addr):
    tmp_data = ""
    try:
        print('connection from', client_addr)

        # Receive the data in small chunks and retransmit it
        while True:
            data = con.recv(RECV_LENGTH)
            data_str = ""
            if data:
                data_str = data.decode("ascii")
                printerr('received "%s" from client' % data_str)
                if data_str == "clean":
                    clean_clients(clients)
                    print_clients(clients)
                elif data_str == "list":
                    send_string(con, return_clients(clients))
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
                index = clients.index(con)
                clients[index] = None
                break

    finally:
        print_clients(clients)
        con.close()


clients = []
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', 43000)
print('starting up on %s port %s' % server_address, file=sys.stderr)
sock.bind(server_address)
sock.listen(1)

while True:
    print('Waiting for a connection')
    connection, client_address = sock.accept()
    t = threading.Thread(target=connection_life, args=(connection, client_address))
    clients.append(connection)
    t.start()
    time.sleep(0.2)
    print_clients(clients)
