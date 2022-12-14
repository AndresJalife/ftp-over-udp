import click
from lib.tcp_lite import TcpLiteClient
from lib.configuration import DefaultConfiguration
from lib.ftp_protocol import FTPFileMessage

initial_config = DefaultConfiguration()


@click.command()
@click.option("-v", "--verbose", default=initial_config.verbosity, help="increase output verbosity")
@click.option("-q", "--quiet", default=1 - initial_config.verbosity, help="decrease output verbosity")
@click.option("-H", "--host", default=initial_config.host, help="service IP address")
@click.option("-p", "--port", default=initial_config.port, help="service port")
@click.option("-d", "--dst", default="copy", help="dst destination file path")
@click.option("-n", "--name", default="", help="file name")
def main(verbose, quiet, host, port, dst, name):
    """Comando para descargar un archivo mediante custom-ftp"""
    socket = TcpLiteClient((host, port), verbosity=1 + verbose - quiet, ack_type=initial_config.send_type)
    if not socket.connect():
        return
    msg = FTPFileMessage(name, FTPFileMessage.FTP_TYPE_DOWNLOAD, bytes(), False)
    socket.send(msg.encode())
    msg = socket.receive()
    msg = FTPFileMessage.decode(msg)
    if msg.type == FTPFileMessage.FTP_TYPE_DOWNLOAD and not msg.error:
        try:
            file = open(dst + "/" + "copy_" + name, "wb")
            file.write(msg.payload)
            file.close()
            print("File downloaded")
        except Exception as e:
            print(e)
            print("ERROR: Could not write file copy_" + name)
    elif msg.error:
        print("ERROR: File not found")
    socket.shutdown()


if __name__ == "__main__":
    main()
