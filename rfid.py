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
            print(clientAddress)
            if(data==b'RfidNumber'):
                server.sendto(rfid,clientAddress)
        except Exception as e:
            print(e)
    server.close() 

rfid = b"" 
isRunning = True
com = input("Enter Serial com port of rfid device:")
threading.Thread(target=serveRfids).start()
try:
    s = serial.Serial(com)
    try:
        while True:
            #rfid=b"1234567891"
            rfid = s.readline()[1:11]
            print(rfid)
    except KeyboardInterrupt:
        isRunning=False
        s.close()
except Exception as e:
    print(e)
    isRunning=False
    

