import socket
import sys


# who client connects to
target_host = socket.gethostbyname(socket.gethostname())
target_port = 8082


def connect():

    # create a socket object
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # connect the client
    s.connect((target_host, target_port))
    while True:
        try:

            # send some data
            s.send(b"#>")
            # receive some data
            r = s.recv(4096).decode()
            print(r)

        except Exception as e:
            print(b"server killed")
            s.close()
            sys.exit()


def main():
    connect()


if __name__ == '__main__':
    main()
