from cgi import print_form
from distutils.command.config import config
from importlib.resources import read_binary
import click
import random
from lib.tcp_lite import TcpLiteServer
from lib.protocol import Protocol

def read_port():
    config_file = open('config.txt','r')
    port = config_file.readline().split('=')[1]
    config_file.close()
    return port


@click.command()
@click.option('-v', '--verbose', default=1, help='increase output verbosity')
@click.option('-q', '--quiet', default=1, help='decrease output verbosity')
@click.option('-H', '--host', default=1, help='service IP address')
@click.option('-p', '--port', default=read_port, help='service port')
@click.option('-s', '--storage', default='files', help='storage dir path')

def main(verbose, quiet, host, port, storage):
    """Comando para comenzar el servidor del custom-ftp"""
    server = TcpLiteServer((port, 10563))
    for sock in server.listen():
        msg = None
        msg = sock.receive().decode('ASCII')
        if msg[0] == Protocol.DOWNLOAD_METHOD:
            file = open(storage + '/' + msg[1:], 'rb')
            sock.send(Protocol.DOWNLOAD_OK.encode('ASCII'))
            byte = file.read()
            sock.send(byte)
            print('Read')
        else:
            sock.send(Protocol.DOWNLOAD_ERROR.encode('ASCII') + ('File Not Found').encode('ASCII'))
            print('Error')

if __name__ == '__main__':
    main()

