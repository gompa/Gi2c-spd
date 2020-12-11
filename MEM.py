#!/usr/bin/env python

try:
    from smbus2 import SMBus
    #print('\nModule was installed')
except ImportError:
    print('\nWe need smbus2 to run, pip3 install smbus2')


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

def printcrc(final):
    #crc=hex(crcb(final[:117]))
    #print(crc[2:])
    #crcbyte123=int('0x'+crc[4:],16)
    #crcbyte124=int(crc[:4],16)
    #print(hex(crcbyte123))
    #print(hex(crcbyte124))
    print("original CRC= "+hex(final[124]) + hex(final[123]).strip("0x") )
    #print(hex(final[123]))



	

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
        #print(args.writecas)
        count=4
        totalcas=0
        for cas in args.writecas.replace(','," ").replace("cl","").split( ):
                print(cas)
                totalcas= totalcas+True<<int(cas)-count
                print(bin(totalcas))
    #print(bin(int(hex(int('11010100', 2)),16)))
    #print(bin(int(hex(int(bincaslow, 2)),16)))
    
    #print(bin(11010100))
    #print(bytes.fromhex(bytes(final[:116])))

def showCASenabled(final):
    bincaslow=bin(final[14])
    #print(bincaslow)
    count=4
    print("cas latencys enabled:")
    for cl in reversed(bincaslow[2:]):
        print("cl"+str(count)+"="+cl)
        
        count=count+1
        

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
    
    printcrc(final)
	#show info
    showpartnumber(final)
    showCASenabled(final)
    if args.writecas:
        writecas(final, args)

    print("min cycle time tckmin= "+str(final[12])+"ns")
    print("min cas latency= "+str(final[16])+"ns") 
    print("RAS# to CAS#  delay time =  "+str(final[18])+"MBT")
    #print(hex(final[18]))
    print("min row precharge delay time trpmin =  "+str(final[20])+"MBT")
#    print( hex(binascii.crc_hqx(bytes.fromhex(" ".join(final[:116]))),0))
    #print(final)
    final=spdcrc(final)
    #writebus(0,0x50,final)
main()
