from distutils.command.config import config
from importlib.resources import read_binary
from threading import Thread
import click
from lib.tcp_lite import TcpLiteServer
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
    msg = FTP_file_message.decode(msg)
    if msg.type == FTP_TYPE_DOWNLOAD:
        with open(storage + '/' + msg.file_name, 'rb') as file:
            bytes_to_send = file.read()
            sock.send(FTP_file_message(msg.file_name, FTP_TYPE_DOWNLOAD, bytes_to_send, False).encode())
            print('File sent')
    elif msg.type == FTP_TYPE_UPLOAD:
        try:
            with open(storage + '/' + msg.file_name, 'wb') as file:
                file.write(msg.payload)
                sock.send(FTP_file_message("", FTP_TYPE_UPLOAD, bytes(), False).encode())
                print("Uploaded: {}".format(msg.file_name))
        except:
            sock.send(FTP_file_message("", FTP_TYPE_UPLOAD, bytes(), True).encode())
            print("There was a error with the file")
    else:
        sock.send(FTP_file_message("", FTP_TYPE_UPLOAD, "Method Not Found".encode("ASCII"), True).encode())
        print('Error - Method not found.')


if __name__ == '__main__':
    main()

