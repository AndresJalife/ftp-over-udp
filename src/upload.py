import click
from lib.tcp_lite import TcpLiteClient
import random

@click.command()
@click.option('-v', '--verbose', default=1, help='increase output verbosity')
@click.option('-q', '--quiet', default=1, help='decrease output verbosity')
@click.option('-H', '--host', default=1, help='service IP address')
@click.option('-p', '--port', default=1, help='service port')
@click.option('-s', '--src', default=1, help='source file path')
@click.option('-n', '--name', default=1, help='file name')

IP = "127.0.0.1"
PORT = 10563

def main(verbose, quiet, host, port, src, name):
    """Comando para cargar un archivo mediante custom-ftp"""
    socket = TcpLiteClient(('127.0.0.1', 10563), ack_type=TcpLiteClient.GO_BACK_N)
    if not socket.connect():
        return
    while True:
        string = None
        for i in range(10):
            string = socket.receive().decode('ascii')
            print(f'Received {string}')
            socket.send((string + random.choice('ABCDEFGHIJKLPQRSTXYZ')).encode('ASCII'))

#     Se conecta al servidor con ftp_lite
#     Se carga el archivo q hay que subir
#     Se lo pasa al ftp_lite
#     Ver si fue exitoso o falló

if __name__ == '__main__':
    main()
