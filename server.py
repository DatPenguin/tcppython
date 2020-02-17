import socket
import sys
import threading


def printerr(text):
    print(text, file=sys.stderr)


def connection_life(con, client_addr):
    tmp_data = ""
    try:
        print('connection from', client_addr)

        # Receive the data in small chunks and retransmit it
        while True:
            data = con.recv(4096)
            print('received "%s"' % data.decode("ascii"))
            if data:
                tmp_data += data.decode("ascii")
                # Bricolage : ne fonctionne pas si la taille du paquet est un multiple de 4096
                if len(data.decode("ascii")) != 4096:
                    print('sending data back to the client')
                    con.sendall(tmp_data.encode("ascii"))
                    tmp_data = ""
            else:
                print('no more data from', client_addr)
                break

    finally:
        # Clean up the connection
        con.close()


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', 43000)
print('starting up on %s port %s' % server_address, file=sys.stderr)
sock.bind(server_address)
sock.listen(1)

while True:
    printerr('Waiting for a connection')
    connection, client_address = sock.accept()
    threading.Thread(target=connection_life, args=(connection, client_address)).start()
