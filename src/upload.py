import click
from lib.tcp_lite import TcpLiteClient
from lib.protocol import Protocol
from lib.ftp_protocol import FTP_file_message

NAME_MAX_LENGTH = 20

@click.command()
@click.option('-v', '--verbose', default=1, help='increase output verbosity')
@click.option('-q', '--quiet', default=1, help='decrease output verbosity')
@click.option('-H', '--host', default=1, help='service IP address')
@click.option('-p', '--port', default=1, help='service port')
@click.option('-s', '--src', default="", help='source file path')
@click.option('-n', '--name', default="", help='file name')

# IP = "127.0.0.1"
# PORT = 10563

def main(verbose, quiet, host, port, src, name):
    """Comando para cargar un archivo mediante custom-ftp"""
    socket = TcpLiteClient(('127.0.0.1', 10563), ack_type=TcpLiteClient.GO_BACK_N)
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


#     Se conecta al servidor con ftp_lite
#     Se carga el archivo q hay que subir
#     Se lo pasa al ftp_lite
#     Ver si fue exitoso o falló

if __name__ == '__main__':
    main()
