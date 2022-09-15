

def plaint_text(message):

    return "1"+message

def substitute(message,n):

    answer=""
    for i in range(len(message)):
        if(message[i].isupper()):
            answer+=chr(ord('A')+(ord(message[i])+(n)-ord('A'))%26)
        elif(message[i].islower()):
            answer+=chr(ord('a')+(ord(message[i])+(n)-ord('a'))%26)

        elif(message[i].isdigit()):
            answer+=str((int(message[i])+(n))%10)
        else:
            answer+=message[i]
    if(n<10):
        return "20"+str(n)+answer
    return "2"+str(n)+answer

def transpose(message):

    
    answer=""
    temp=""
    for i in range(len(message)):
        if(message[i]==' '):
            answer+=temp[::-1]+" "
            temp=""
        else:
            temp+=message[i]
        # answer+=message[len(message)-i-1]
    if(len(temp)>0):
        answer=answer+temp[::-1]

    return "3"+answer

#Decoding the substitution cipher
def decode_offset(message,n):
    answer=""
    for i in range(len(message)):
        if(message[i].isupper()):
            answer+=chr(ord('A')+(ord(message[i])-(n)-ord('A'))%26)
        elif(message[i].islower()):
            answer+=chr(ord('a')+(ord(message[i])-(n)-ord('a'))%26)

        elif(message[i].isdigit()):
            answer+=str((int(message[i])-(n))%10)
        else:
            answer+=message[i]
    return answer
