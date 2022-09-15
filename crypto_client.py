from socket import *
import os
import crypto    #imported the crypto header file
import random
import base64

#local host is defined by this address
servername='127.0.0.1'

#Defined the server port number
serverPort=12345

#Defining TCP socket with IPV4 address

clientsocket=socket(AF_INET,SOCK_STREAM)

#Establishing the connection with the server
clientsocket.connect((servername,serverPort))

print("Connection established")

#keeps count of number of queries made so far 
i=0
while True:
    i+=1

    #Taking the input command
    message=input("Query"+str(i)+": ")

    #Randomly selecting the type of encyrption to use among: plain text, substitute and transpose method
    crypto_layer=random.randint(1,3)

    #Encrypted Message sent via socket
    server_message=""

    #Contains file name in case of upload/download
    filename=""
    
    #Encrypting the message to be sent into the string 'server_message'
    offset=random.randint(0,25)
    if(crypto_layer==1):
        server_message=crypto.plaint_text(message)
    elif(crypto_layer==2):
        server_message=crypto.substitute(message, offset)
    else:
        server_message=crypto.transpose(message)

    #Sending the encrypted command to the server
    clientsocket.sendto(server_message.encode(), (servername,serverPort))
    #Start receiving the file in case of download
    if(message[0:3]=="DWD"):
        filename=message[4:]

        try:
            #try to open file as binary. If it already exists, it doesn't download it again
            file=open(filename,'rb')
            while(clientsocket.recv(2048)):
                continue
            file.close()
            print("NOK, file already exists")
            clientsocket.shutdown(SHUT_RD)
            clientsocket.close()
            clientsocket=socket(AF_INET,SOCK_STREAM)
            clientsocket.connect((servername,serverPort))
            reply,serveraddress=clientsocket.recvfrom(2048)
            continue
        except:
            filesize,serveraddress=clientsocket.recvfrom(2048)
            filesize=filesize.decode()
            filesize=int(filesize)
            file=open(filename,'wb')

            #do nothing if file size to be received is of 0 bytes
            if(filesize==0):
                file.close()
                os.remove(filename)
                
                clientsocket.shutdown(SHUT_RD)
                clientsocket.close()
                clientsocket=socket(AF_INET,SOCK_STREAM)
                clientsocket.connect((servername,serverPort))

            while filesize!=0:
                
                #receive file packets from the server
                packet=clientsocket.recv(8388608)

                #if packet is empty, it means all packets are received. So break out of the loop
                if not packet:
                    # print("Writing Completed")
                    file.close()
                    clientsocket.shutdown(SHUT_RD)
                    clientsocket.close()
                    clientsocket=socket(AF_INET,SOCK_STREAM)
                    clientsocket.connect((servername,serverPort))
                    break
                
                file_packet=packet
                packet=packet.decode()
                file_packet=base64.b64encode(file_packet)

                #Decode the ecrypted bytes and store it in 'file_packet'
                if(crypto_layer==1):
                    file_packet=(crypto.plaint_text(packet)[1:]).encode()
                elif(crypto_layer==2):
                    file_packet=(crypto.decode_offset(packet,offset)).encode()
                else:
                    file_packet=(crypto.transpose(packet)[1:]).encode()
                packet=packet.encode()
                file_packet=base64.b64decode(file_packet)
                # print("received packet : ", packet[:10])
                # print("actual packet : ",file_packet[:10])

                #use the bytes to write the file in binary
                file.write(file_packet)
            
            


    #Start sending the file in case of upload
    if(message[0:3]=="UPD"):
        filename=message[4:]

        
        try:
            file=open(filename)
            file.seek(0,os.SEEK_END)
            filesize=int(file.tell())
            clientsocket.sendto(str(file.tell()).encode(),(servername,serverPort))
            # print("File size to be sent ", (file.tell()))
            file.close()
            file=open(filename,'rb')


            while True:

                packet=file.read(8388608)
                
                if not packet:
                
                    # print("Sending Completed")
                    
                    file.close()

                    clientsocket.shutdown(SHUT_WR)
                    clientsocket.close()
                    clientsocket=socket(AF_INET,SOCK_STREAM)
                    clientsocket.connect((servername,serverPort))
                    break

                packet_to_be_sent=""
                
                packet=base64.b64encode(packet)
                packet=packet.decode()
               
                if(crypto_layer==1):
                    packet_to_be_sent=crypto.plaint_text(packet)[1:]
                elif(crypto_layer==2):
                    
                    packet_to_be_sent=crypto.substitute(packet, offset)[3:]
                else:
                    
                    packet_to_be_sent=crypto.transpose(packet)[1:]
                
                packet=packet.encode()
                packet=base64.b64decode(packet)    
                packet_to_be_sent=packet_to_be_sent.encode()    

                # print("Original packet: ",packet[:10])
                # print("Sending packet : ", packet_to_be_sent[:10])
                clientsocket.sendall(packet_to_be_sent)
        #if file doesn't exist then do the following:
        except:
            clientsocket.shutdown(SHUT_WR)
            clientsocket.close()
            clientsocket=socket(AF_INET,SOCK_STREAM)
            clientsocket.connect((servername,serverPort))
            print("NOK, file doesn't exist on client")
            reply,serveraddress=clientsocket.recvfrom(2048)
            continue


    #Final message (Actual data for CWD and LS, and status update for CD,DWD,UPD)
    reply,serveraddress=clientsocket.recvfrom(2048)

    reply=reply.decode()

    terminal_message=""
    #Decrypting the message received from the server
    if(reply[0]=='1'):

        terminal_message=reply[1:]
    elif(reply[0]=='2'):
        
        terminal_message=crypto.decode_offset(reply[3:],int(reply[1:3]))
    else:

        terminal_message=crypto.transpose(reply[1:])[1:]
    
    print(terminal_message)
    #Close connection when "close" command is sent to the server. In this case server replies "Connection Closed"
    if(terminal_message=="Connection Closed"):
        break

clientsocket.close()




