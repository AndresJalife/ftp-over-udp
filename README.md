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

El comando download descarga 
