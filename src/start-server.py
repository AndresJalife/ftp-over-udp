import click
import random
from lib.tcp_lite import TcpLiteServer
from lib.protocol import Protocol

@click.command()
@click.option('-v', '--verbose', default=1, help='increase output verbosity')
@click.option('-q', '--quiet', default=1, help='decrease output verbosity')
@click.option('-H', '--host', default=1, help='service IP address')
@click.option('-p', '--port', default=1, help='service port')
@click.option('-s', '--storage', default='files', help='storage dir path')

def main(verbose, quiet, host, port, storage):
    """Comando para comenzar el servidor del custom-ftp"""
    server = TcpLiteServer(('127.0.0.1', 10563), ack_type=TcpLiteServer.GO_BACK_N)
    for sock in server.listen():
        msg = sock.receive().decode('ASCII')
        if msg[0] == Protocol.DOWNLOAD_METHOD:
            file = open(storage + '/' + msg[1:], 'rb')
            sock.send(Protocol.DOWNLOAD_OK.encode('ASCII'))
            byte = file.read()
            sock.send(byte)
            print('Read')
        elif msg[0] == Protocol.UPLOAD_METHOD:
            file = open("copia" + msg[1:msg.index("/")], 'x')
            file.write(msg[msg.index("/") + 1:])
        else:
            sock.send(Protocol.DOWNLOAD_ERROR.encode('ASCII') + ('File Not Found').encode('ASCII'))
            print('Error')

if __name__ == '__main__':
    main()
