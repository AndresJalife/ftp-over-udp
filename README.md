# ftp-over-udp

ftp-over-udp es un proyecto que realiza download y upload de archivos con una arquitectura cliente-servidor.  
Por medio de diferentes comandos, el cliente puede subir, descargar un archivo o ver cuales son los archivos que se encuentran disponibles en el servidor.  

El envio de paquetes se realiza sobre una version simplificada de TCP que llamamos TcpLite. Esta garantiza que los archivos lleguen ordenados y en su totalidad, lo que lo hace un protocolo fiable. Sin embargo, no garantiza control de congestion ni de flow, como si lo hace TCP.  

Utilizamos la libreria de click para facilitar el uso de parametros en los comandos.  
https://click.palletsprojects.com/en/8.1.x/  


A continuacion, se encuentran los comandos explicados en detalle:   

### LIST  

El comando list lista todos los archivos que estan disponibles en el servidor y pueden ser descargados por el cliente.
Se ejecuta con el siguiente comando:  

    python3 src/list.py 

Options:  

    -v, --verbose INTEGER  

Aumenta la verbosidad del cliente TCP. Hay mas logs para explicar en detalle el proceso.  

    -q, --quiet INTEGER  

Disminuye la verbosidad del cliente TCP. Hay menos logs para explicar en detalle el proceso.  

    -H, --host TEXT  

La direccion IP a la que se conectara el cliente. Por defecto, se utiliza la direccion especificada en config.txt.  

    -p, --port INTEGER  

El puerto al que se conectara el cliente. Por defecto, se utiliza el puerto especificado en config.txt.  

    --help   

### DOWNLOAD  

El comando download descarga un archivo del servidor al cliente. A la descarga realizada se le agrega el prefijo 'copy_'. 
Se ejecuta con el siguiente comando:  

    python3 src/download.py -n file_name  

Options:  

    -v, --verbose INTEGER  

Aumenta la verbosidad del cliente TCP. Hay mas logs para explicar en detalle el proceso.  

    -q, --quiet INTEGER  

Disminuye la verbosidad del cliente TCP. Hay menos logs para explicar en detalle el proceso.  

    -H, --host TEXT  

La direccion IP a la que se conectara el cliente. Por defecto, se utiliza la direccion especificada en config.txt.  

    -p, --port INTEGER  

El puerto al que se conectara el cliente. Por defecto, se utiliza el puerto especificado en config.txt.  

    -d, --dst TEXT  

La carpeta de destino a donde se copiara el archivo. Por defecto, se copia en la carpeta 'copy'.  

    -n, --name TEXT  

Nombre del archivo a descargar. Unico parametro obligatorio del comando.  

    --help  

### UPLOAD  

El comando upload carga un archivo del cliente al servidor.  
Se ejecuta con el siguiente comando:  

    python3 src/upload.py -n file_name  

Options:  

    -v, --verbose INTEGER  

Aumenta la verbosidad del cliente TCP. Hay mas logs para explicar en detalle el proceso.  

    -q, --quiet INTEGER  

Disminuye la verbosidad del cliente TCP. Hay menos logs para explicar en detalle el proceso.  

    -H, --host TEXT  

La direccion IP a la que se conectara el cliente. Por defecto, se utiliza la direccion especificada en config.txt.  

    -p, --port INTEGER  

El puerto al que se conectara el cliente. Por defecto, se utiliza el puerto especificado en config.txt.  

    -s, --src TEXT  

La carpeta de origen de donde se carga el archivo. Por defecto, se utiliza la raiz.  

    -n, --name TEXT  

Nombre del archivo a descargar. Unico parametro obligatorio del comando.  

    --help  

### SERVIDOR  

Levanta el servidor para que los clientes puedan conectarse a el y transferir los archivos correspondientes.  
Se ejecuta con el siguiente comando:  

    python3 src/start-server.py

Options:  

    -v, --verbose INTEGER  

Aumenta la verbosidad del cliente TCP. Hay mas logs para explicar en detalle el proceso.  

    -q, --quiet INTEGER  

Disminuye la verbosidad del cliente TCP. Hay menos logs para explicar en detalle el proceso.  

    -H, --host TEXT  

La direccion IP a la que se conectara el cliente. Por defecto, se utiliza la direccion especificada en config.txt.  

    -p, --port INTEGER  

El puerto al que se conectara el cliente. Por defecto, se utiliza el puerto especificado en config.txt.  

    -s, --storage TEXT  

La carpeta donde se guardan los archivos. Por defecto, se utiliza la carpeta especificada en config.txt.   

    --help  

### config.txt  

El archivo de configuracion establece las configuraciones por defecto. El mismo contiene informacion sobre:  

    host=127.0.0.1
    storage=files
    port=10563
    verbosity=0
    send_type=gbn

Los primeros cuatro parametros fueron explicados anteriormente.  
El send_type establece el protocolo de transporte. Puede ser Stop & Wait o Go Back N.
