import click
from lib.tcp_lite import TcpLiteServer
from lib.protocol import Protocol

NAME_MAX_LENGTH = 20

@click.command()
@click.option('-v', '--verbose', default=1, help='increase output verbosity')
@click.option('-q', '--quiet', default=1, help='decrease output verbosity')
@click.option('-H', '--host', default=1, help='service IP address')
@click.option('-p', '--port', default=1, help='service port')
@click.option('-s', '--storage', default='files', help='storage dir path')

def main(verbose, quiet, host, port, storage):
    """Comando para comenzar el servidor del custom-ftp"""
    server = TcpLiteServer(('127.0.0.1', 10563), ack_type=TcpLiteServer.GO_BACK_N)
    for sock in server.listen():
        msg = sock.receive()
        if msg[0] == 0:
            msg = msg.decode('ASCII')
            file = open(storage + '/' + msg[1:], 'rb')
            sock.send(Protocol.DOWNLOAD_OK.encode('ASCII'))
            byte = file.read()
            sock.send(byte)
            print('Read')
        elif msg[0] == 1:
            try:
                name = ""
                for i in range(1, NAME_MAX_LENGTH + 1):
                    name = name + chr(msg[i])
                for i in range(len(name) - 1, -1, -1):
                    if name[i] != "0":
                        break
                    name = name[:len(name) - 1]
                file = open(storage + '/' + name, 'wb')
                file.write(msg[NAME_MAX_LENGTH + 1:])
            except:
                print("No se pudo crear el archivo")
        else:
            sock.send(Protocol.DOWNLOAD_ERROR.encode('ASCII') + ('File Not Found').encode('ASCII'))
            print('Error')

#     Comienza a escuchar
#     Se fija si los mensajes entrantes son upload, download o listar
#     Si es download
#        se lee el file name
#        si no existe manda mensaje de error
#        si existe, lo envía

#     Si es upload
#        le llega el archivo
#        con el nombre al principio
#        arma el archivo (junta payload con nombre) y lo guarda

#     Si es listar
#        devuelve
#

if __name__ == '__main__':
    main()
