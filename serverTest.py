
import socket

with socket.socket(family=socket.AF_INET,type=socket.SOCK_STREAM) as sock:
    sock.bind(("127.0.0.1",3001))
    sock.listen()
    while 1:
        connection,addr=sock.accept()
        while 1:
            data=connection.recv(1024)
            if not data: break
            else: print(data.decode())
        
        connection.close()
