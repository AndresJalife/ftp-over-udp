import os
from distutils.command.config import config
from importlib.resources import read_binary
from threading import Thread
import click
from lib.tcp_lite import TcpLiteServer
from lib.configuration import DefaultConfiguration
from lib.ftp_protocol import FTPFileMessage
import sys

initial_config = DefaultConfiguration()


@click.command()
@click.option("-v", "--verbose", default=1, help="increase output verbosity")
@click.option("-q", "--quiet", default=1, help="decrease output verbosity")
@click.option("-H", "--host", default=initial_config.host, help="service IP address")
@click.option("-p", "--port", default=initial_config.port, help="service port")
@click.option(
    "-s", "--storage", default=initial_config.storage, help="storage dir path"
)
def main(verbose, quiet, host, port, storage):
    """Comando para comenzar el servidor del custom-ftp"""
    server = TcpLiteServer((port, host), verbosity=1 + verbose - quiet)
    listen_thread = Thread(target=_listen, args=[server, storage], daemon=True)
    listen_thread.start()
    _close_server(server)


def _listen(server, storage):
    for sock in server.listen():
        receive_thread = Thread(target=_receive_msg, args=(sock, storage), daemon=True)
        receive_thread.start()


def _close_server(server):
    msg = input("Write quit to close the server\n")
    while True:
        if msg == "quit":
            server.shutdown()
            print("The server has been closed")
            sys.exit()


def _receive_msg(sock, storage):
    msg = sock.receive()
    msg = FTPFileMessage.decode(msg)
    if msg.type == FTPFileMessage.FTP_TYPE_DOWNLOAD:
        try:
            with open(storage + "/" + msg.file_name, "rb") as file:
                bytes_to_send = file.read()
                sock.send(
                    FTPFileMessage(
                        msg.file_name,
                        FTPFileMessage.FTP_TYPE_DOWNLOAD,
                        bytes_to_send,
                        False,
                    ).encode()
                )
                print("File sent")
        except:
            sock.send(
                FTPFileMessage(type=FTPFileMessage.FTP_TYPE_UPLOAD, error=True).encode()
            )
            print("File not found.")
    elif msg.type == FTPFileMessage.FTP_TYPE_UPLOAD:
        try:
            with open(storage + "/" + msg.file_name, "wb") as file:
                file.write(msg.payload)
                sock.send(
                    FTPFileMessage(
                        "", FTPFileMessage.FTP_TYPE_UPLOAD, bytes(), False
                    ).encode()
                )
                print("Uploaded: {}".format(msg.file_name))
        except:
            sock.send(
                FTPFileMessage(
                    "", FTPFileMessage.FTP_TYPE_UPLOAD, bytes(), True
                ).encode()
            )
            print("There was a error with the file")
    elif msg.type == FTPFileMessage.FTP_TYPE_LIST:
        files = os.listdir(storage)
        payload = (",".join(files)).encode("ASCII")
        print(",".join(files))
        sock.send(
            FTPFileMessage(type=FTPFileMessage.FTP_TYPE_LIST, payload=payload).encode()
        )
    else:
        sock.send(
            FTPFileMessage(
                "",
                FTPFileMessage.FTP_TYPE_UPLOAD,
                "Method Not Found".encode("ASCII"),
                True,
            ).encode()
        )
        print("Error - Method not found.")


if __name__ == "__main__":
    main()
