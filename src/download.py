import click
from lib.tcp_lite import TcpLiteClient
from lib.protocol import Protocol


@click.command()
@click.option('-v', '--verbose', default=1, help='increase output verbosity')
@click.option('-q', '--quiet', default=1, help='decrease output verbosity')
@click.option('-H', '--host', default=1, help='service IP address')
@click.option('-p', '--port', default=1, help='service port')
@click.option('-d', '--dst', default='copy', help='dst destination file path')
@click.option('-n', '--name', default='', help='file name')

def main(verbose, quiet, host, port, dst, name):
    """Comando para descargar un archivo mediante custom-ftp"""
    socket = TcpLiteClient(('127.0.0.1', 10563), ack_type=TcpLiteClient.STOP_AND_WAIT)
    if not socket.connect():
        return
    msg = Protocol.DOWNLOAD_METHOD.encode('ASCII') + (name).encode('ASCII')
    socket.send(msg)
    msg = socket.receive().decode('ASCII')
    print('OK:', msg)
    if msg == Protocol.DOWNLOAD_OK:
        file = open(dst + '/' + 'copy_' + name, 'w')
        byte = socket.receive().decode('ASCII')
        file.write(byte)
        file.close()
        print('OK')
    elif msg == Protocol.DOWNLOAD_ERROR:
        print('ERROR:', msg[1:])



    # click.echo(f"Hello {name}!")

if __name__ == '__main__':
    main()
