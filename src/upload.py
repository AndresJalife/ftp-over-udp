import click
from lib.tcp_lite import TcpLiteClient
from lib.protocol import Protocol
import random
from lib.configuration import DefaultConfiguration

initial_config = DefaultConfiguration()

NAME_MAX_LENGTH = 20
from lib.ftp_protocol import FTP_file_message

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
        FTP_f_m = FTP_file_message(name, Protocol.UPLOAD_METHOD, f.read(), "")
        msg = FTP_f_m.encode()
        socket.send(msg)
        f.close()
        byte = socket.receive().decode('ASCII')
        if byte == Protocol.UPLOAD_OK:
            print("The file {} has been uploaded".format(name))
        else:
            print("The file {} could not be uploaded".format(name))
    except:
        print("There was a error with the file")

    #socket.shutdown()

if __name__ == '__main__':
    main()
