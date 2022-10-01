import click
from lib.tcp_lite import TcpLiteClient
import random
from lib.configuration import DefaultConfiguration

initial_config = DefaultConfiguration()

@click.command()
@click.option('-v', '--verbose', default=1, help='increase output verbosity')
@click.option('-q', '--quiet', default=1, help='decrease output verbosity')
@click.option('-H', '--host', default=initial_config.host, help='service IP address')
@click.option('-p', '--port', default=initial_config.port, help='service port')
@click.option('-s', '--src', default=1, help='source file path')
@click.option('-n', '--name', default=1, help='file name')
def main(verbose, quiet, host, port, src, name):
    """Comando para cargar un archivo mediante custom-ftp"""
    socket = TcpLiteClient((port, host), ack_type=TcpLiteClient.GO_BACK_N)
    if not socket.connect():
        return
    while True:
        string = None
        for i in range(10):
            string = socket.receive().decode('ascii')
            print(f'Received {string}')
            socket.send((string + random.choice('ABCDEFGHIJKLPQRSTXYZ')).encode('ASCII'))

if __name__ == '__main__':
    main()
