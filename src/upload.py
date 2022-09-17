import click
from lib.tcp_lite import TcpLiteSocket

@click.command()
@click.option('-v', '--verbose', default=1, help='increase output verbosity')
@click.option('-q', '--quiet', default=1, help='decrease output verbosity')
@click.option('-H', '--host', default=1, help='service IP address')
@click.option('-p', '--port', default=1, help='service port')
@click.option('-s', '--src', default=1, help='source file path')
@click.option('-n', '--name', default=1, help='file name')
def main(verbose, quiet, host, port, src, name):
    """Comando para cargar un archivo mediante custom-ftp"""
    socket = TcpLiteSocket(('127.0.0.1', 10563))
    if not socket.connect():
        return
    data, addr = socket.try_receive()
    while (data, addr) == (None, None):
        data, addr = socket.try_receive()
    print(data.decode('ascii'))

if __name__ == '__main__':
    main()
