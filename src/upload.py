import click
from lib.tcp_lite import TcpLiteClient
import random
from lib.configuration import DefaultConfiguration

initial_config = DefaultConfiguration()

from lib.ftp_protocol import FTPFileMessage


@click.command()
@click.option("-v", "--verbose", default=1, help="increase output verbosity")
@click.option("-q", "--quiet", default=1, help="decrease output verbosity")
@click.option("-H", "--host", default=initial_config.host, help="service IP address")
@click.option("-p", "--port", default=initial_config.port, help="service port")
@click.option("-s", "--src", default="", help="source file path")
@click.option("-n", "--name", default="", help="file name")
def main(verbose, quiet, host, port, src, name):
    """Comando para cargar un archivo mediante custom-ftp"""
    socket = TcpLiteClient((port, host), verbosity=1 + verbose - quiet)
    if not socket.connect():
        return
    try:
        with open(src + "/" + name, "rb") as f:
            msg = FTPFileMessage(
                name, FTPFileMessage.FTP_TYPE_UPLOAD, f.read(), False
            ).encode()
            socket.send(msg)
            msg = FTPFileMessage.decode(socket.receive())
            if not msg.error:
                print("The file {} has been uploaded".format(name))
            else:
                print("The file {} could not be uploaded".format(name))
    except:
        print(f"There was a error with the file {src + '/' + name}")

    socket.shutdown()


if __name__ == "__main__":
    main()
