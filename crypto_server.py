from socket import *
import crypto
import base64
import os
from os import getcwd,listdir,chdir
s=socket(AF_INET, SOCK_STREAM)
serverport=12345
#bind the port number to the server
s.bind(('',serverport))

s.listen(1)
print("Server is listening")
while True:

    #accept the TCP connection request and create the connection socket
    connectionsocket,addr=s.accept()
    print("connection established")

    
    while True:
        #Receive the command from the client in encrypted form
        message,clientaddress=connectionsocket.recvfrom(2048)

        message=message.decode()

        print("Recieved message by server = ", message)
        print("Crypto layer = ", message[0])

        actual_message=""

        #Decrypt the command received and store it in 'actual_message'
        if(message[0]=='1'):

            actual_message=message[1:]

        elif(message[0]=='2'):

            actual_message=crypto.decode_offset(message[3:],int(message[1:3]))
            
        else:

            actual_message=crypto.transpose(message[1:])[1:]

        print("Actual message = ",actual_message)
        
        #Reply to send to the client (Status in case of DWD and UPD commands)
        reply=""

        #send the "Connection Closed" message to client if the client wants to break the connection
        if(actual_message=="close"):
            reply="Connection Closed"
            if(message[0]=='1'):
                reply=crypto.plaint_text(reply)
            elif(message[0]=='2'):
                reply=crypto.substitute(reply,int(message[1:3]))
            else:
                reply=crypto.transpose(reply)
            
            connectionsocket.send(reply.encode())
            break
        
        #Replies for CWD, LS, CD commands and file transfer code for DWD and UPD
        if(actual_message[0:3]=="CWD"):
            reply=getcwd()
        elif(actual_message[0:2]=="LS"):
            items=listdir()

            reply=" Items : "

            for item in items:
                reply+=item+" , "
        elif(actual_message[0:2]=="CD"):
            reply="OK"

            # current_directory=getcwd()
            # new_directory=path.join(current_directory,message[3:])
            try:
                print("Arguement for chrdir = ",actual_message[3:])
                chdir(actual_message[3:])
                # reply="OK"
            except:
                reply="NOK"

        elif(actual_message[0:3]=="DWD"):
            
            reply="OK"
            
            try:
                #Compute the filesize and send it to the client as a message
                filename=actual_message[4:]
                file=open(filename,'rb')
                file.seek(0,os.SEEK_END)
                filesize=int(file.tell())
                connectionsocket.send(str(filesize).encode())
                print("File size to be sent ", (filesize))
                file.close()

                file=open(actual_message[4:],"rb")
                while True:
                    
                    #Receive the encrypted packets
                    packet=file.read(8388608)
                    if not packet:
                        print("Sending Completed")
                        connectionsocket.close()
                        break
                    packet_to_be_sent=""
                    packet=base64.b64encode(packet)
                    packet=packet.decode()
                   
                    #Encrypt the packets before sending them to the client
                    if(message[0]=='1'):
                        packet_to_be_sent=crypto.plaint_text(packet)[1:]
                    elif(message[0]=='2'):
                        
                        packet_to_be_sent=crypto.substitute(packet, int(message[1:3]))[3:]
                    else:
                        packet_to_be_sent=crypto.transpose(packet)[1:]
                    
                    packet=packet.encode()
                    packet=base64.b64decode(packet)   
                    packet_to_be_sent=packet_to_be_sent.encode()     
                    
                    print("Original packet: ",packet[:10])
                    print("Sending packet : ", packet_to_be_sent[:10])
                    connectionsocket.sendall(packet_to_be_sent)
                    
                file.close()
                #Connection is broken and restablished 
                connectionsocket,addr=s.accept()
                print("Connection restablished")
            #If the file is not present in the server
            except:
                reply="NOK, file doesn't exist on server"
                
                connectionsocket.send(str(0).encode())
                connectionsocket.close()
                connectionsocket,addr=s.accept()
                print("Connection restablished")
            

        elif(actual_message[0:3]=="UPD"):
            reply="OK"

            #Not upload if the file already exists in the server
            try:
                with open(actual_message[4:],"r") as file:
                    while connectionsocket.recv(2048):
                        continue
                    reply="NOK, file already exists in the server"
            except:
                filesize,clientaddress=connectionsocket.recvfrom(2048)
                filesize=filesize.decode()
                if(filesize==''):
                    filesize=0
                filesize=int(filesize)
                if(filesize==0):
                    reply="NOK, file doesn't exist on client"
                    connectionsocket.close()
                else:
                    file= open(actual_message[4:],"wb") 

                print("File size to be received = ",filesize)
                while filesize!=0:

                    #Receive the encrypted packets
                    packet=connectionsocket.recv(8388608)

                    if not packet:
                        print("Writing Completed")
                        file.close()
                        break

                    #Decrypt the received bytes and store it in 'file_packet'
                    file_packet=packet
                    packet=(packet).decode()
                    if(message[0]=='1'):
                        file_packet=(crypto.plaint_text(packet)[1:]).encode()
                    elif(message[0]=='2'):
                        file_packet=(crypto.decode_offset(packet,int(message[1:3]))).encode()
                    else:
                        file_packet=(crypto.transpose(packet)[1:]).encode()
                    packet=packet.encode()
                    
                    file_packet=base64.b64decode(file_packet)
                    print("received packet : ", packet[:5])
                    print("actual packet: ",file_packet[:5])
                    file.write(file_packet)
            #Connection is resetablished after disconnecting
            connectionsocket,addr=s.accept()
            print("Connection restablished")
        
        #If an invalid command is sent to the server
        else: 
            reply="Not a Valid Query"
        
        #Reply is the message that needs to be sent to the client
        print("Server reply without encryption : ",reply)

        #Encrypt the reply before sending
        if(message[0]=='1'):
            reply=crypto.plaint_text(reply)
        elif(message[0]=='2'):
            reply=crypto.substitute(reply,int(message[1:3]))
        else:
            reply=crypto.transpose(reply)
        
        connectionsocket.send(reply.encode())

    connectionsocket.close()



