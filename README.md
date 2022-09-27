# ftp-over-udp

usando click

https://click.palletsprojects.com/en/8.1.x/

paquetes grandes se dropean mas facil elegimos paquetes chico 4096  

### DOWNLOAD PROTOCOL  

Sends:  

+-----------+  
|   METHOD  |  
+-----------+  
| FILE NAME |  
+-----------+  

METHOD: 1 byte. Has a value of 0  
FILE NAME: Name of the file that wants to be downloaded  

Recieves:  

+-----------+  
|   OK   |  
+-----------+  
| DATA CHUNK |  
+-----------+  

OK: 1 byte. Flag indicating if the file can be downloaded  
DATA CHUNK: The file. If there was an error it contains the error message  