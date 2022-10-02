import click
from lib.tcp_lite import TcpLiteClient
from lib.configuration import DefaultConfiguration
from lib.ftp_protocol import FTP_file_message

initial_config = DefaultConfiguration()

@click.command()
@click.option('-v', '--verbose', default=1, help='increase output verbosity')
@click.option('-q', '--quiet', default=1, help='decrease output verbosity')
@click.option('-H', '--host', default=initial_config.host, help='service IP address')
@click.option('-p', '--port', default=initial_config.port, help='service port')
@click.option('-d', '--dst', default='copy', help='dst destination file path')
@click.option('-n', '--name', default='', help='file name')


def main(verbose, quiet, host, port, dst, name):
    """Comando para descargar un archivo mediante custom-ftp"""
    socket = TcpLiteClient((port, host), ack_type=TcpLiteClient.GO_BACK_N)
    if not socket.connect():
        return
    msg = FTP_file_message(name, FTP_file_message.FTP_TYPE_DOWNLOAD, bytes(), False)
    socket.send(msg.encode())
    msg = socket.receive()
    msg = FTP_file_message.decode(msg)
    if msg.type == FTP_file_message.FTP_TYPE_DOWNLOAD and not msg.error:
        try:
            file = open(dst + '/' + 'copy_' + name, 'wb')
            # byte = socket.receive()
            file.write(msg.payload)
            file.close()
            print('OK')
        except:
            print('ERROR: Could not write file copy_' + name)
    elif msg.error:
        print('ERROR:', msg[1:])
    socket.shutdown()

if __name__ == '__main__':
    main()
