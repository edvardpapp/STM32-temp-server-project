import socket
import sys
from datetime import datetime

def closeServer():
    clientsocket.close()
    serversocket.close()
    file.close()
# Define the host and port to listen on
host = socket.gethostbyname(socket.gethostname())
#host = '192.168.1.249'  #otthoni wifi
#host = '192.168.0.102'  #koli wifi
port = 9999             #random port

#open database
file = open('/Users/dominikpapp/Desktop/egyetem/6felev/onlab/web/data.txt', 'a')
print("Appending data to: data.txt")

# Create a TCP socket object
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.setblocking(True)
# Bind the socket to the host and port
try:
    serversocket.bind((host, port))
except Exception as fail:
    print(str(fail))
    print("NOT ABLE TO BIND PORT")
    print("EXITING...")
    sys.exit()

print(f"Server IP address: {host}")
print(f"Server port number: {port}")
# Start listening for incoming connections
serversocket.listen()  #one connection enabled
print(f"Listening on {host}:{port}...")

# Wait for a client to connect
clientsocket, addr = serversocket.accept()
print(f"Got a connection from {addr}")
# Receive data from the client until a space character is encountered
data = b""
message = ""

while True:
    chunk = clientsocket.recv(1024)
    data += chunk
    if b"q" in data:
        message = data.decode()
        message = message.replace('q', '\r')
        data = b""
        print(f"Received message: {message}")
    if "exit" in message:
        break
    else:# Get current date and time
        current_datetime = datetime.now()
        # Format the date and time as a string
        formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
        file.write(formatted_datetime + "  " + message)
        file.flush()       #'live' data writing

#close everthing
closeServer()
