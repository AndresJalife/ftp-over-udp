from cgi import print_form
from distutils.command.config import config
from importlib.resources import read_binary
import click
import random
from lib.tcp_lite import TcpLiteServer
from lib.protocol import Protocol

def read_port():
    """Read the config file and get the port"""
    config_file = open('config.txt','r')
    lines = config_file.readlines()
    for line in lines:
        port_line = line.split('=')
        if port_line[0] == 'port':
            port = port_line[1].rstrip()
    config_file.close()
    return port

def read_host():
    """Read the config file and get the host"""
    config_file = open('config.txt','r')
    lines = config_file.readlines()
    for line in lines:
        host_line = line.split('=')
        if host_line[0] == 'host':
            host = host_line[1]
    config_file.close() 
    return host 

@click.command()
@click.option('-v', '--verbose', default=1, help='increase output verbosity')
@click.option('-q', '--quiet', default=1, help='decrease output verbosity')
@click.option('-H', '--host', default=read_host, help='service IP address')
@click.option('-p', '--port', default=read_port, help='service port')
@click.option('-s', '--storage', default='files', help='storage dir path')

def main(verbose, quiet, host, port, storage):
    """Comando para comenzar el servidor del custom-ftp"""
    server = TcpLiteServer((port, int(host)))
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

