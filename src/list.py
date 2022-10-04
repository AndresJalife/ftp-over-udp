import click
from lib.tcp_lite import TcpLiteClient
from lib.ftp_protocol import FTPFileMessage
from lib.configuration import DefaultConfiguration

initial_config = DefaultConfiguration()


@click.command()
@click.option("-v", "--verbose", default=initial_config.verbosity, help="increase output verbosity")
@click.option("-q", "--quiet", default=1 - initial_config.verbosity, help="decrease output verbosity")
@click.option("-H", "--host", default=initial_config.host, help="service IP address")
@click.option("-p", "--port", default=initial_config.port, help="service port")
def main(verbose, quiet, host, port):
    """Comando para listar los archivos en el servidor"""
    socket = TcpLiteClient((host, port), verbosity=1 + verbose - quiet, ack_type=initial_config.send_type)
    if not socket.connect():
        return

    try:
        packet = FTPFileMessage(type=FTPFileMessage.FTP_TYPE_LIST)
        socket.send(packet.encode())
        response = FTPFileMessage.decode(socket.receive())
        files = response.payload.decode("ASCII").split(",")
        print("El servidor contiene los siguientes archivos:")
        for file in files:
            print(file)
    except Exception as e:
        print(e)
        print("Failed to list files from FTP server.")

    socket.shutdown()


if __name__ == "__main__":
    main()
