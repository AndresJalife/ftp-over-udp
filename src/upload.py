import click
from lib.tcp_lite import TcpLiteClient
from lib.protocol import Protocol
import random

@click.command()
@click.option('-v', '--verbose', default=1, help='increase output verbosity')
@click.option('-q', '--quiet', default=1, help='decrease output verbosity')
@click.option('-H', '--host', default=1, help='service IP address')
@click.option('-p', '--port', default=1, help='service port')
@click.option('-s', '--src', default="", help='source file path')
@click.option('-n', '--name', default="", help='file name')

def main(verbose, quiet, host, port, src, name):
    """Comando para cargar un archivo mediante custom-ftp"""
    socket = TcpLiteClient(('127.0.0.1', 10563), ack_type=TcpLiteClient.GO_BACK_N)
    if not socket.connect():
        return
    try:
        f = open(src + "/" + name, 'r')
        print(src + "/" + name)
        msg = (Protocol.UPLOAD_METHOD + name + "/" + f.read()).encode('ASCII')
        socket.send(msg)
        f.close()
    except:
        print("No se pudo abrir el archivo")
    #socket.shutdown()

if __name__ == '__main__':
    main()
