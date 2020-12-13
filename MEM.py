#!/usr/bin/env python

try:
    from smbus2 import SMBus
    #print('\nModule was installed')
except ImportError:
    print('\nWe need smbus2 to run\n pip3 install smbus2 as root')


import time
import binascii
import argparse
VERBOSE=0
POLYNOMIAL = 0x1021
PRESET = 0

def _initial(c):
    crc = 0
    c = c << 8
    for j in range(8):
        if (crc ^ c) & 0x8000:
            crc = (crc << 1) ^ POLYNOMIAL
        else:
            crc = crc << 1
        c = c << 1
    return crc

_tab = [ _initial(i) for i in range(256) ]

def _update_crc(crc, c):
    cc = 0xff & c

    tmp = (crc >> 8) ^ cc
    crc = (crc << 8) ^ _tab[tmp & 0xff]
    crc = crc & 0xffff
    #print (crc)

    return crc

def crc(str):
    crc = PRESET
    for c in str:
        crc = _update_crc(crc, ord(c))
    return crc

def crcb(i):
    crc = PRESET
    for c in i:
        #print(c)
        crc = _update_crc(crc, c)
    return crc

def printcurrentcrc(final):
    #crc=hex(crcb(final[:117]))
    #print(crc[2:])
    #crcbyte123=int('0x'+crc[4:],16)
    #crcbyte124=int(crc[:4],16)
    #print(hex(crcbyte123))
    #print(hex(crcbyte124))
    print("Current CRC= "+padhex(final[124]) + padhex(final[123])[2:] )
    #print(hex(final[123]))

def padhex(hexunpadded):
    vis = hex(hexunpadded)
    printr = '0x' + vis[2:].zfill(2)
    return(printr)
	

def spdcrc(final):
    crc=hex(crcb(final[:117]))
    #print(crc[2:])
    crcbyte123= int('0x'+crc[4:],16)
    crcbyte124=int(crc[:4],16)
    #print(hex(crcbyte123))
    #print(crcbyte124)
    #print(final[123])
    #print(final[124])
    final[123]=crcbyte123
    final[124]=crcbyte124
    
    return(final)

def writecas(final,args):
        print("writecas")
        caswant=args.replace("cl","").split(" ")
        caswant=[int(x) for x in caswant if x]
        print(caswant)
        #caswant=map(caswant,int)
        #caswant=list(caswant)
        #print(caswant)
        
        count=4
        casoffset=4
        casbin=0
        cascount=0
        casstring=""
        totalcasarray=16 
        while cascount < 16:
            if cascount+casoffset in caswant:
                casstring=casstring+"1"
            else:
                casstring=casstring+"0"
            #print(casstring)
            cascount=cascount+1
        
        print("casstirng"+casstring)
        print("caslow byte= "+casstring[:8][::-1])
        print("cashigh byte= "+casstring[8:][::-1])
        print("cashigh byte int= "+ str(hex(int("0b"+casstring[8:][::-1],2))))
        print("caslow byte int= "+ str(hex(int("0b"+casstring[:8][::-1],2))))
        #print(final)
        final[14]=int("0b"+casstring[:8][::-1],2)
        final[15]=int("0b"+casstring[8:][::-1],2)
        # ~ print(final)
        return(final)
        # ~ for cas in args.writecas.replace(','," ").replace("cl","").split( ):

                # ~ #totalcas= totalcas+True<<int(cas)-count
                # ~ #print(bin(totalcas))
                # ~ print("incasloop:")
                # ~ print(cas)
                # ~ if cas == count:
                    # ~ print(str(casbin)+str(1))
                    # ~ casbin=int(str(casbin)+str(1),2)
                # ~ else:
                   # ~ casbin=int(str(casbin)+str(0),2)
                   
                   
                # ~ count= count+1
                # ~ #print(cas)
                # ~ print(bin(casbin))
                # ~ print(bin(int("0b"+str(casbin),2)))
        # ~ print(bin(casbin)) 
    #print(bin(int(hex(int('11010100', 2)),16)))
    #print(bin(int(hex(int(bincaslow, 2)),16)))
    
    #print(bin(11010100))
    #print(bytes.fromhex(bytes(final[:116])))

def readmincasdelay(final):
    mincasdelay=final[16]*0.1250
    print("min cas latency= "+str(mincasdelay)+"ns") 
    print()


def readtckmin(final):
    #print('-------readtckmin-----')
    tckmin=final[12]
    tckminoffset=final[34]
    #print(tckminoffset)
    print("tckmin: " + str(tckmin * 0.1250 + tckminoffset) +"ns")
    if hex(tckmin) == "0x14":
        print("DDR3-800 clockspeed=400mhz")
    if hex(tckmin) == "0xf":
        print("DDR3-1066 clockspeed=533mhz")
    if hex(tckmin) == "0xc":
        print("DDR3-1333 clockspeed=667mhz")
    if hex(tckmin) == "0xa":
        print("DDR3-1600 clockspeed=800mhz")
    if hex(tckmin) == "0x9" and hex(tckminoffset) == "0xCA":
        print("DDR3-1866 clockspeed=933mhz")
    if hex(tckmin) == "0x8" and hex(tckminoffset) == "0xC2":
        print("DDR3-2133 clockspeed=1067mhz")    
    #print("min cycle time tckmin= "+str(final[12])+"ns")
    #print(hex(final[12]))
    

def writetckmin(final, args):
    print("writetckmin----")
    print(args)
    print(final[12])
    return(final)

def showCASenabled(final):
    # ~ print(bincashigh)
    bincaslow=format(final[14], '#010b')
    bincashigh=format(final[15], '#010b')
    # ~ print(bincaslow)
    #print(bincashigh)
    # ~ print(hex(final[14]))
    # ~ print(hex(final[15]))
    totalenabled=""
    count=0
    offset=4
    print("cas latencys enabled:")
    for cl in reversed(bincaslow[2:]):
        #print("cl"+str(count)+"="+cl)
        if count == 7:
            totalenabled= totalenabled+ " "+"cl"+str(count+offset)+"="+cl+"\n"
        else:
            totalenabled= totalenabled+ " "+"cl"+str(count+offset)+"="+cl
        count=count+1
    for cl in reversed(bincashigh[2:]):
        if count != 18:
            if count == 7:
                totalenabled= totalenabled+ " "+"cl"+str(count+offset)+"="+cl+"\n"
            else:
                totalenabled= totalenabled+ " "+"cl"+str(count+offset)+"="+cl
            #print("cl"+str(count)+"="+cl)
            #totalenabled= totalenabled+ " "+"cl"+str(count)+"="+cl
        count=count+1
    #print(count)
    print(totalenabled)
    
    
def readbus(bus=0,address=0x50):
    data=[]
    offset=0
    count=0
    while len(data) < 256:
            #i2caddress = 0x50  # Address of MCP23017 device
            with SMBus(0) as bus:
                bus.pec = 1
                # Read a block of 16 bytes from address 80, offset 0
                block = bus.read_i2c_block_data(address, offset, 32)
                #print(block)
                #block ='0x' + block[2:].zfill(2)
                # Returned value is a list of 32 bytes
                data.extend(block)
                offset=offset+32
                #print(block)
                count= count+1
    #print(data)
    #3print(hex(data))
    final=[]
    visual=[]
    #print("-------------------data------------------")
    #print(data)
    for test in data:
        vis = hex(test)
        printr = '0x' + vis[2:].zfill(2)
        final.append(int(printr,16))
    #print(count)
    return(final)


def showpartnumber(final):
    partnumber=final[128:]
    partnumber=partnumber[:145]
    stripdpartnumber=bytes(partnumber)[2: -2].decode().replace('\x00','')
    print("partnumber: "+stripdpartnumber)


def writebus(busaddr=0,address=0x50,data=[]):
        flashblocksize=16
        offset=0
        print("datacount"+str(len(data)))
        print("flashing: ")
        while offset < 255:
                print("blocks left: "+str(len(data)))
                #print("curdata")
                #setup data blocks
                curdata=data[:flashblocksize]
                #remove flashed blocks from list
                del data[:flashblocksize]
                count=0
                for hexvalue in curdata:
                       # print(hexvalue)
                        curdata[count]=hexvalue
                        count=count+1        
                with SMBus(busaddr) as bus:
                    bus.pec = 1
                    time.sleep(0.2)
                    # Write a block of flashblock size  bytes to address from offset 
                    #bus.write_i2c_block_data(address, offset, curdata)
                    #time.sleep(0.2)
                    
                    offset=offset+flashblocksize
                  


def main():
    '''
    Main program function
    '''
    # Define registers values from datasheet
    parser = argparse.ArgumentParser()
    parser.add_argument("--writetckmin",
                        help="set min cycle time tckmin  byte 12 in ns exaple: --writetckmin 100ns")
    parser.add_argument("--writecas",
                        help="set enabled CAS latencys in byte 14")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="increase output verbosity")
    args = parser.parse_args()
    
    
    #answer = args.square**2
    if args.verbose:
        print("verbose")
        VERBOSE=1
       # print("the square of {} equals {}".format(args.square, answer))
    else:
        VERBOSE=0

    #read bus, defaults bus=0 adress=0x50
    final=readbus()

    #calculate crc and write to final
    
    printcurrentcrc(final)
	#show info
    showpartnumber(final)
    showCASenabled(final)


    readtckmin(final)
    
    
    
    
    #print("min cas latency= "+str(final[16])+"ns") 
    readmincasdelay(final)
    print("RAS# to CAS#  delay time =  "+str(final[18])+"MBT")
    #print(hex(final[18]))
    print("min row precharge delay time trpmin =  "+str(final[20])+"MBT")
#    print( hex(binascii.crc_hqx(bytes.fromhex(" ".join(final[:116]))),0))
    #print(final)
    if args.writetckmin:
        final=writetckmin(final, args.writetckmin)  
        print("newcas")
           
    
    
    if args.writecas:
        final=writecas(final, args.writecas)  
        print("newcas")
        showCASenabled(final)  
    final=spdcrc(final)
    printcurrentcrc(final)
    #writebus(0,0x50,final)
main()
