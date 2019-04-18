import serial
import socket
import threading
import time

def serveRfids():
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    serverIp = ("127.0.0.1",8999)
    server.bind(serverIp)
    while isRunning:
        try:
            data, clientAddress = server.recvfrom(10)
            print("client Hit:",clientAddress)
            if(data==b'RfidNumber'):
                server.sendto(rfid,clientAddress)
        except Exception as e:
            print(e)
    server.close() 

rfid = b"" 
isRunning = True
com = input("Enter Serial com port of rfid device:")
s = serial.Serial(com)
threading.Thread(target=serveRfids).start()
print("Rfid server running on server 127.0.0.1:8999.press ctrl+c to exit")
try:
    while True:
        try:
            #rfid=b"1234567891"
            rfid = s.readline()[1:11]
            print("Detected Rf card:",rfid)
        except Exception as e:
            print(e)
except KeyboardInterrupt:
    isRunning=False
    s.close()
    

