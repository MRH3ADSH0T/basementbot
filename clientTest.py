
import socket

HOST,PORT="127.0.0.1",42069
ADDRESS=(HOST,PORT)

def client(data:str):
    with socket.socket(family=socket.AF_INET,type=socket.SOCK_STREAM) as connect:
        #print(f"connecting to {ADDRESS}...")
        connect.connect(ADDRESS)
        #print("connected!")
        connect.send(data.encode())
        if data=="off": return None
        return connect.recv(4096).decode()

if __name__=="__main__":
    while 1:
        data=client(input("> "))
        #print("finished send")
        if not data:
            print("killed")
            break
        else:
            print(data)
