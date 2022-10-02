import click
from lib.tcp_lite import TcpLiteClient
from lib.protocol import Protocol
from lib.ftp_protocol import FTP_message


@click.command()
@click.option('-v', '--verbose', default=1, help='increase output verbosity')
@click.option('-q', '--quiet', default=1, help='decrease output verbosity')
@click.option('-H', '--host', default=10563, help='service IP address')
@click.option('-p', '--port', default='127.0.0.1', help='service port')
@click.option('-d', '--dst', default='copy', help='dst destination file path')
@click.option('-n', '--name', default='', help='file name')


def main(verbose, quiet, host, port, dst, name):
    """Comando para descargar un archivo mediante custom-ftp"""
    socket = TcpLiteClient((port, host), ack_type=TcpLiteClient.GO_BACK_N)
    if not socket.connect():
        return
    msg = FTP_message(Protocol.DOWNLOAD_METHOD, name, '')
    socket.send(msg.encode())
    msg = socket.receive().decode('ASCII')
    if msg == Protocol.DOWNLOAD_OK:
        try:
            file = open(dst + '/' + 'copy_' + name, 'wb')
            byte = socket.receive()
            file.write(byte)
            file.close()
            print('OK')
        except:
            print('ERROR: Could not write file copy_' + name)
    elif msg == Protocol.DOWNLOAD_ERROR:
        print('ERROR:', msg[1:])
    socket.shutdown()

if __name__ == '__main__':
    main()
