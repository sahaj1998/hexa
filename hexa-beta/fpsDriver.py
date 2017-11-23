__author__ = 'guru'
import serial
import binascii
import RPi.GPIO as GPIO

serialport = serial.Serial("/dev/ttyAMA0", timeout=10)
serialport.baudrate = 9600


GPIO.setmode(GPIO.BCM)
GPIO.setup(8, GPIO.OUT) # Red
GPIO.setup(11, GPIO.OUT) # Green
# buzzer
# light 2

GPIO.output(11,0)
GPIO.output(8,0)



def fpsTransmitter(data):
    question =  binascii.unhexlify(data)
    print("string trans >",data)
    serialport.write(question)

def fpsReceiver():
    str = binascii.hexlify(serialport.read(12)).decode("utf-8")
    print("string res   >",str)
    return str

def fpsReceiverWithExtraData():
    str = binascii.hexlify(serialport.read(12)).decode("utf-8")
    if str[12:16] == "0500":
        str = str + binascii.hexlify(serialport.read(5)).decode("utf-8")
    print("string res   >",str)
    return str

def fpsTemplateReceiver():
    str = binascii.hexlify(serialport.read(12)).decode("utf-8")
    if str[12:16] == "5006":
        str = str + binascii.hexlify(serialport.read(1616)).decode("utf-8")
    print("string res   >",str)
    return str

def checkSum(dataString,write):
    totalSum = 0
    for i in range(0,22):
        if( i%2 == 0):
            totalSum += int(dataString[i:i+2],16)
    checkSum = dataString[22:24]
    tempString = hex(totalSum)[::-1]     #[::-1] reverses the string
    if((tempString[0:2][::-1] == checkSum) or (write == 1)):
        chkString = tempString[0:2][::-1]
        return (1,chkString)
    else:
        chkString = '0'
        return (0,chkString)

def dataCompiler(channel,command,param11,param12,param21,param22,dataSize11,dataSize12,dataSize21,dataSize22,errCode):
    All = (channel+command+param11+param12+param21+param22+dataSize11+dataSize12+dataSize21+dataSize22+errCode+'00')
    temp = checkSum(All,1)
    if( temp[0] == 1):
        All = All[0:22]
        All+=temp[1]
        return All
    else:
        return 0


#0x50 command starts the registration by finger info
def initiateRegistration(mobileNumber):
    data = dataCompiler('00','50','ff','ff','00','00','05','00','00','00','00')
    fpsTransmitter(data+mobileNumber)
    str=fpsReceiver()
    chk=checkSum(str,0)
    if (chk[0] == 1):
        if(str[2:4] == '50' and str[4:6] == 'ff' and str[6:8] == 'ff' and str[20:22] == '00'):
            return (1,'00')
        else:
            return (0,'00')
    else:
        return (0,str[20:22])

#0x51 command ends registration
def terminateRegistration():
    data = dataCompiler('00','51','00','00','00','00','00','00','00','00','00')
    fpsTransmitter(data)
    str=fpsReceiver()
    chk=checkSum(str,0)
    if (chk[0] == 1):
        if(str[2:4] == '51' and str[4:6] == 'ff' and str[6:8] == 'ff' and str[20:22] == '00'):
            return (1,'00')
        else:
            return (0,'00')
    else:
        return (0,str[20:22])


#0x19 command for including 2nd finger
def continueRegistration():
    data = dataCompiler('00','19','00','00','00','00','00','00','00','00','00')
    fpsTransmitter(data)
    str = fpsReceiver()
    chk = checkSum(str,0)
    if (chk[0] == 1):
        if(str[2:4] == '19' and str[4:6] == '00' and str[6:8] == '00' and str[20:22] == '00'):
            return (1,'00')
        else:
            return (0,'00')
    else:
        return (0,str[20:22])

#0xA3 command for getting input from finger print
def identify():
    str=fpsReceiverWithExtraData()

    chk = checkSum(str,0)
    if (chk[0] == 1):
        if(str[2:4] == 'a3' and str[4:6] == 'ff' and str[6:8] == 'ff' and str[12:14] == '05' and str[20:22] =='00'):
            return (1,str[24:34])
        else:
            return (0,'00')
    else:
        return (0,str[20:22])


def getTemplateGenerator(mobileNumber):
    data = dataCompiler('00','73','ff','ff','00','00','05','00','00','00','00')
    fpsTransmitter(data+mobileNumber)
    str = fpsTemplateReceiver()
    chk=checkSum(str[0:24],0)
    if (chk[0] == 1):
        if(str[2:4] == '73' and str[4:6] == 'ff' and str[6:8] == 'ff' and str[3232:3242] == mobileNumber):
            #template1 = str[32:3232]
            #template2 = str[1632:3232]

            return (1,str[32:1632],str[1632:3232])
        else:
            return (0,'00')
    else:
        return (0,str[20:22])

def putTemplateGenerator():

    print("function under construction")

def autoIdentifyStart():
    ledSoundFunction(1,1)

    print("Auto identify started")

def autoIdentifyStop():
    ledSoundFunction(0,1)

    print("Auto identify stopped")

def identifySingle():
    data = dataCompiler('00','56','00','00','00','00','00','00','00','00','00')
    fpsTransmitter(data)
    str=fpsReceiverWithExtraData()
    chk=checkSum(str,0)
    if (chk[0] == 1):
        if(str[2:4] == '56' and str[4:6] == 'ff' and str[6:8] == 'ff' and str[12:14] == '05' and str[20:22] =='00'):
            return (1,str[24:34])
        else:
            return (0,'00')
    else:
        return (0,str[20:22])


def makeTemplateStart():
    data = dataCompiler('00', '35', '00', '00', '00', '00', '00', '00', '00', '00', '00')
    fpsTransmitter(data)
    str = fpsReceiver()
    if checkSum(str, 0)[0]:
        if str[2:4] == '35' and str[20:22] == '00':
            return 1
        else:
            return 0
    else:
        return 0

def makeTemplateContinue():
        data = dataCompiler('00', '36', '00', '00', '00', '00', '00', '00', '00', '00', '00')
        fpsTransmitter(data)
        str = fpsReceiver()
        if checkSum(str, 0)[0]:
            if str[2:4] == '36' and str[20:22] == '00':
                return 1
            else:
                return 0
        else:
            return 0


def ledSoundFunction(putstate, colour):
    if putstate == 1:
        if colour == 1:
            GPIO.output(11, 1)
        if colour == 0:
            GPIO.output(8, 1)
    else:
        if colour == 1:
            GPIO.output(11, 0)
        if colour == 0:
            GPIO.output(8, 0)

if __name__ == "__main__":
    print("1. for normal method reg\n2. for checking template presence")
    op = input()
    if op == '1':
        print("Enter Mobile Number:")
        phn = input()
        if identifySingle()[0] == 0:
            if initiateRegistration(str(phn))[0]:
                print ("input any char to continue")
                input()
                if terminateRegistration()[0]:
                    #if continueRegistration()[0]:
                    print("done")
        else:
            print("user already exist")
    elif op == '2':
        print("place your finger")

