import os
import sys
import errno
import socket
import optparse


def request(host, port, child_num, con_num, bytes):
    # spawn child_num children processes
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((host, port))
                sock.sendall(str(bytes).encode())

                data = sock.recv(bytes)
                print(data)
                if len(data) != bytes:
                    raise Exception('Server returned only %d bytes' % len(data))

                sock.close() # TIME_WAIT state on the client



def main():
    parser = optparse.OptionParser()
    parser.add_option(
        '-i', '--host', dest='host', help='Hostname or IP address')

    parser.add_option('-p', '--port', dest='port', type='int', help='Port')

    parser.add_option(
        '-c', '--child-num', dest='childnum', type='int', default=5,
        help='Number of children to spawn. Default is 5'
        )
    parser.add_option(
        '-t', '--con-num', dest='connum', type='int', default=500,
        help='Number of connections to establish. Default is 5'
        )
    parser.add_option(
        '-b', '--bytes', dest='bytes', type='int', default=3000,
        help='Number of bytes to request. Default is 3000'
        )

    options, args = parser.parse_args()

    if not (options.host and options.port):
        parser.print_help()
        sys.exit(1)

    request(options.host, options.port,
            options.childnum, options.connum, options.bytes)

if __name__ == '__main__':
    main()
