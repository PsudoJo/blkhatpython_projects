import socket
import threading
import sys


# output starter
star = "[*]"


def main():
    # establish socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # bind IP to Port on s
    s.bind((socket.gethostname(), 8082))
    # establish 5 connections
    s.listen(5)
    print(f'{star}Listening for incoming connection...')
    # endlessly listen

    # accept connections
    client, address = s.accept()
    # output accepted connection from port & IP
    print(f'{star}Accepted connection from {address[0]}:{address[1]}')
    # output number of threads minus server thread
    print(f"{star} user count: ", threading.active_count())
    # creates thread for client handling & passes to client handler
    client_handler = threading.Thread(target=handle_client, args=(client,))
    client_handler.start()


def handle_client(client_socket):
    cmd_buffer = b''
    while True:

        try:
            client_socket.send(b'#>')
            while '\n' not in cmd_buffer.decode():
                cmd_buffer += client_socket.recv(64)
            response = cmd_buffer.decode()
            if response:
                client_socket.send(response.encode())
            cmd_buffer = b''
        except KeyboardInterrupt:
            print(f'server killed')
            client_socket.close()
            sys.exit()


if __name__ == '__main__':
    main()
