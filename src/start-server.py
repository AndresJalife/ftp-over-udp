import click
import random
from lib.tcp_lite import TcpLiteServer

@click.command()
@click.option('-v', '--verbose', default=1, help='increase output verbosity')
@click.option('-q', '--quiet', default=1, help='decrease output verbosity')
@click.option('-H', '--host', default=1, help='service IP address')
@click.option('-p', '--port', default=1, help='service port')
@click.option('-s', '--storage', default=1, help='storage dir path')

def main(verbose, quiet, host, port, storage):
    """Comando para comenzar el servidor del custom-ftp"""
    server = TcpLiteServer(('127.0.0.1', 10563))
    for sock in server.listen():
        string = ''
        for i in range(10):
            sock.send((string + random.choice('abcdefghijklpqrtsxyz')).encode('ASCII'))
            string = sock.receive().decode('ASCII')
            print(f'Received {string}')

if __name__ == '__main__':
    main()
