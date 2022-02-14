import argparse
import socket
import shlex
import subprocess
import sys
import textwrap
import threading


# default values
targ = socket.gethostbyname(socket.gethostname())
port = "5555"

# function that receives command


# def execute(cmd):
#     # removes white space before and after a string
#     cmd = cmd.strip()
#     if not cmd:
#         return
#     # helps with output parsing by class
#     output = subprocess.check_output(
#         shlex.split(cmd), stderr=subprocess.STDOUT)
#     # return decoded output
#     return output.decode()

# NetCat functionality


class NetCat:
    # initialize variables locally within class
    def __init__(self, args, buffer=None):
        self.args = args
        self.buffer = buffer
        # create socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # delegates 2 methods
    def run(self):
        # if listener , call listen method, else call send method
        if self.args.listen:
            self.listen()
        else:
            self.send()

    # send method
    def send(self):
        # connect to target and port specified by argparser
        self.socket.connect((self.args.target, self.args.port))
        # if i have a buffer send that to target first
        if self.buffer:
            self.socket.send(self.buffer)
        # try/except -> allow user to manually cut connection
        try:
            # start a loop to receive data from target
            while True:
                recv_len = 1
                response = ''
                while recv_len:
                    data = self.socket.recv(4096)
                    recv_len = len(data)
                    response += data.decode()
                    # if no more data received break out of loop
                    if recv_len < 4096:
                        break
                # otherwise we print response data and pause to get an interactive input, send input & continue loop
                if response:
                    print(response)
                    buffer = input('> ')
                    buffer += '\n'
                    self.socket.send(buffer.encode())
        except KeyboardInterrupt:
            print('User terminated')
            self.socket.close()
            sys.exit()
    # if program is run as a listener

    def listen(self):
        # binds to target and port, listens in loop
        self.socket.bind((self.args.target, self.args.port))
        self.socket.listen(5)
        while True:
            client_socket, _ = self.socket.accept()
            # passing connected socket to handle method
            client_thread = threading.Thread(
                target=self.handle, args=(client_socket,)
            )
            client_thread.start()
    '''
    logic to perform file uploads, execute commands, & create interactive shell
    program can perform these tasks as a listener
    '''

    def handle(self, client_socket):
        if self.args.execute:
            output = execute(self.args.execute)
            client_socket.send(output.encode())

        elif self.args.upload:
            file_buffer = b''
            while True:
                data = client_socket.recv(4096)
                if data:
                    file_buffer += data
                else:
                    break
            with open(self.args.upload, 'wb') as f:
                f.write(file_buffer)
            message = f'Saved file {self.args.upload}'
            client_socket.send(message.encode())

        elif self.args.command:
            cmd_buffer = b''
            while True:
                try:
                    client_socket.send(b'#>')
                    while '\n' not in cmd_buffer.decode():
                        cmd_buffer += client_socket.recv(64)
                    response = execute(cmd_buffer.decode())
                    if response:
                        client_socket.send(response.encode())
                    cmd_buffer = b''
                except Exception as e:
                    print(f'server killed {e}')
                    self.socket.close()
                    sys.exit()


if __name__ == '__main__':
    # calls module to accept arguments for parser
    parser = argparse.ArgumentParser(
        description='BHP Net Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        # for user to see usage
        epilog=textwrap.dedent(f''' Example:
            netcat.py -t {targ} -p {port} -l -c # command shell 
            netcat.py -t {targ} -p {port} -l -u=myexample.txt #upload to file 
            netcat.py -t {targ} -p {port} -l -e=\"cat /etc/passwd\" #execute command
            echo 'ABC' | ./netcat.py -t {targ} -p 135 # echo text to server port 135
            netcat.py -t {targ} -p {port} # connect to server   
        '''))
    # set how I want the program to behave
    parser.add_argument('-c', '--command',
                        action='store_true', help='command_shell')
    parser.add_argument('-e', '--execute', help='execute specified command')
    parser.add_argument('-l', '--listen', action='store_true', help='listen')
    parser.add_argument(
        '-t', '--target', default='192.168.1.108', help='specified IP')
    parser.add_argument('-u', '--upload', help='upload file')
    parser.add_argument('-p', '--port', type=int,
                        default=5555, help='specified port')
    args = parser.parse_args()

    # if setting up listener buffer with empty string
    if args.listen:
        buffer = ''
    # if not listener send buffer content from stdin
    else:
        buffer = sys.stdin.read()

    nc = NetCat(args, buffer.encode())

    # run netcat class
    nc.run()
