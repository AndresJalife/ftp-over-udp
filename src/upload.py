import click
from lib.tcp_lite import TcpLiteClient
from lib.protocol import Protocol
import random
from lib.configuration import DefaultConfiguration

initial_config = DefaultConfiguration()

NAME_MAX_LENGTH = 20

@click.command()
@click.option('-v', '--verbose', default=1, help='increase output verbosity')
@click.option('-q', '--quiet', default=1, help='decrease output verbosity')
@click.option('-H', '--host', default=initial_config.host, help='service IP address')
@click.option('-p', '--port', default=initial_config.port, help='service port')
@click.option('-s', '--src', default="", help='source file path')
@click.option('-n', '--name', default="", help='file name')
def main(verbose, quiet, host, port, src, name):
    """Comando para cargar un archivo mediante custom-ftp"""
    socket = TcpLiteClient((port, host), ack_type=TcpLiteClient.GO_BACK_N)
    if not socket.connect():
        return
    try:
        f = open(src + "/" + name, 'rb')
        print(src + "/" + name)
        for i in range(0, NAME_MAX_LENGTH - len(name)):
            name = name + "0"
        msg = (Protocol.UPLOAD_METHOD.encode('utf-8') + name.encode('utf-8') + f.read())
        socket.send(msg)
        f.close()
    except:
        print("No se pudo abrir el archivo")
    #socket.shutdown()


if __name__ == '__main__':
    main()
