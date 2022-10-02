from distutils.command.config import config
from importlib.resources import read_binary
from threading import Thread
import click
from lib.tcp_lite import TcpLiteServer
from lib.protocol import Protocol
from lib.configuration import DefaultConfiguration

initial_config = DefaultConfiguration()

NAME_MAX_LENGTH = 20
from lib.ftp_protocol import FTP_file_message

FTP_TYPE_DOWNLOAD = 0
FTP_TYPE_UPLOAD = 1

@click.command()
@click.option('-v', '--verbose', default=1, help='increase output verbosity')
@click.option('-q', '--quiet', default=1, help='decrease output verbosity')
@click.option('-H', '--host', default=initial_config.host, help='service IP address')
@click.option('-p', '--port', default=initial_config.port, help='service port')
@click.option('-s', '--storage', default=initial_config.storage, help='storage dir path')

def main(verbose, quiet, host, port, storage):
    """Comando para comenzar el servidor del custom-ftp"""
    server = TcpLiteServer((port, host), ack_type=TcpLiteServer.GO_BACK_N)
    close_thread = Thread(target=_close_server, args=[server],daemon=True)
    close_thread.start()

    for sock in server.listen():
        receive_thread = Thread(target=_receive_msg, args=(sock,storage),daemon=True)
        receive_thread.start()


def _close_server(server):
    msg = input("Write quit to close the server\n")
    while True:
        if(msg=='quit'):
            server.shutdown()
            break
    print('The server has been closed')

def _receive_msg(sock, storage):
    msg = sock.receive()
    if msg[0] == FTP_TYPE_DOWNLOAD:
        msg = msg.decode('ASCII')
        file = open(storage + '/' + msg[1:], 'rb')
        sock.send(Protocol.DOWNLOAD_OK.encode('ASCII'))
        byte = file.read()
        sock.send(byte)
        print('Read')
    elif msg[0] == FTP_TYPE_UPLOAD:
        try:
            FTP_f_m = FTP_file_message("", Protocol.UPLOAD_METHOD, "", "")
            FTP_f_m.decode(msg)
            file = open(storage + '/' + FTP_f_m.file_name, 'wb')
            file.write(FTP_f_m.payload)
            sock.send(Protocol.UPLOAD_OK.encode('ASCII'))
            print("Uploaded: {}".format(FTP_f_m.file_name))
        except:
            print("There was a error with the file")
    else:
        sock.send(Protocol.DOWNLOAD_ERROR.encode('ASCII') + ('File Not Found').encode('ASCII'))
        print('Error')


if __name__ == '__main__':
    main()

