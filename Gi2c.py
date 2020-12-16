#!/usr/bin/env python

try:
    from smbus2 import SMBus
    #print('\nModule was installed')
except ImportError:
    print('\nWe need smbus2 to run\n pip3 install smbus2 as root')


import time
import binascii
import argparse

WRITE=0
READFROMFILE=0
WRITETOFILE=0
POLYNOMIAL = 0x1021
PRESET = 0


def writefile(final,filename):
    with open(filename, 'w') as f:
        for item in final:
            f.write(padhex(item)+" ")
            
            
def readfromfile(filename):
    with open(filename, 'r') as f:
        data=f.read()
        data= data.split(" ")
        data =list(filter(None, data))
        count=0
        final=[]
        for value in data:
            if value != '':
                final.append(int(value,16))

        return(final)



def _initial(c):
    crc = 0
    c = c << 8
    for j in range(8):
        if (crc ^ c) & 0x8000:
            crc = (crc << 1) ^ POLYNOMIAL
        else:
            crc = crc << 1
        c = c << 1
    return(crc)

_tab = [ _initial(i) for i in range(256) ]

def _update_crc(crc, c):
    cc = 0xff & c
    tmp = (crc >> 8) ^ cc
    crc = (crc << 8) ^ _tab[tmp & 0xff]
    crc = crc & 0xffff
    return(crc)

def crc(str):
    crc = PRESET
    for c in str:
        crc = _update_crc(crc, ord(c))
    return(crc)

def crcb(i):
    crc = PRESET
    for c in i:
        crc = _update_crc(crc, c)
    return(crc)

def printcurrentcrc(final):
    print("Current CRC="+padhex(final[124]) + padhex(final[123])[2:] )

def padhex(hexunpadded):
    vis = hex(hexunpadded)
    printr = '0x' + vis[2:].zfill(2)
    return(printr)
	

def spdcrc(final):
    crc=hex(crcb(final[:117]))
    if VERBOSE:
        print(crc)
    crcbyte123= int('0x'+crc[4:],16)
    crcbyte124=int(crc[:4],16)
    final[123]=crcbyte123
    final[124]=crcbyte124
    
    return(final)

def writecas(final,args):
        
        caswant=args.replace("cl","").split(" ")
        caswant=[int(x) for x in caswant if x]
        if VERBOSE:
            print("writecas")
            print(caswant)

        count=4
        casoffset=4
        casbin=0
        cascount=0
        casstring=""
        totalcasarray=16 
        while cascount < 16:
            if cascount == 6:
                casstring=casstring+"1"
                cascount=cascount+1
                continue 
            if cascount+casoffset in caswant:
                casstring=casstring+"1"
            else:
                casstring=casstring+"0"
            cascount=cascount+1
        if VERBOSE:            
            print("casstirng"+casstring)
            print("caslow byte="+casstring[:8][::-1])
            print("cashigh byte="+casstring[8:][::-1])
            print("cashigh byte int="+ str(hex(int("0b"+casstring[8:][::-1],2))))
            print("caslow byte int="+ str(hex(int("0b"+casstring[:8][::-1],2))))
        final[14]=int("0b"+casstring[:8][::-1],2)
        final[15]=int("0b"+casstring[8:][::-1],2)
        return(final)
     
                   
               
def readminrascasdelay(final):
    mincasdelay=final[20]*0.1250
    print("min #ras to #cas delay time="+str(mincasdelay)+"ns") 


def writerastocas(final,rastocas,offset):
    if offset == None:
        offset=0 
    final[20]=int(rastocas)
    final[36]=int(offset)
    return(final)
    

def readmincasdelay(final):
    mincasdelay=final[16]*0.1250
    print("min cas latency="+str(mincasdelay)+"ns") 


def readtckmin(final):
    tckmin=final[12]
    tckminoffset=final[34]
    if VERBOSE:
        print("----tck raw----")
        print(padhex(tckmin))
        print(padhex(tckminoffset))

    if hex(tckmin) == "0x14":
        print("DDR3-800 clockspeed=400mhz")
        print("tckmin: " + str(tckmin * 0.1250 + tckminoffset) +"ns")
    if hex(tckmin) == "0xf":
        print("DDR3-1066 clockspeed=533mhz")
        print("tckmin: " + str(tckmin * 0.1250 + tckminoffset) +"ns")
    if hex(tckmin) == "0xc":
        print("DDR3-1333 clockspeed=667mhz")
        print("tckmin: " + str(tckmin * 0.1250 + tckminoffset) +"ns")
    if hex(tckmin) == "0xa":
        print("DDR3-1600 clockspeed=800mhz")
        print("tckmin: " + str(tckmin * 0.1250 + tckminoffset) +"ns")
    if hex(tckmin) == "0x9" and hex(tckminoffset) == "0xCA":
        print("DDR3-1866 clockspeed=933mhz")
        print("tckmin: " + str(tckmin * 0.1250 + tckminoffset) +"ns")
    if hex(tckmin) == "0x8" and hex(tckminoffset) == "0xC2":
        print("DDR3-2133 clockspeed=1067mhz")    
        print("tckmin: " + str(tckmin * 0.1250 + tckminoffset) +"ns")
    

def writetckmin(final, args , offset=0):
    if offset==None:
        offset=0
    if VERBOSE:        
        print("writetckmin----")
        print(args)
    tckminoffset=int(offset)
    tckmin=int(args)
    print("wanted speed:")
    if hex(tckmin) == "0x14":
        print("DDR3-800 clockspeed=400mhz")
        print("tckmin: " + str(tckmin * 0.1250 + tckminoffset) +"ns")
    if hex(tckmin) == "0xf":
        print("DDR3-1066 clockspeed=533mhz")
        print("tckmin: " + str(tckmin * 0.1250 + tckminoffset) +"ns")
    if hex(tckmin) == "0xc":
        print("DDR3-1333 clockspeed=667mhz")
        print("tckmin: " + str(tckmin * 0.1250 + tckminoffset) +"ns")
    if hex(tckmin) == "0xa":
        print("DDR3-1600 clockspeed=800mhz")
        print("tckmin: " + str(tckmin * 0.1250 + tckminoffset) +"ns")
    if hex(tckmin) == "0x9" and hex(tckminoffset) == "0xCA":
        print("DDR3-1866 clockspeed=933mhz")
        print("tckmin: " + str(tckmin * 0.1250 + tckminoffset) +"ns")
    if hex(tckmin) == "0x8" and hex(tckminoffset) == "0xC2":
        print("DDR3-2133 clockspeed=1067mhz")    
        print("tckmin: " + str(tckmin * 0.1250 + tckminoffset) +"ns")
    final[12]=tckmin
    if VERBOSE:
        print(final[12])
    return(final)

def showCASenabled(final):
    bincaslow=format(final[14], '#010b')
    bincashigh=format(final[15], '#010b')
    totalenabled=""
    count=0
    offset=4
    print("cas latencys enabled:")
    for cl in reversed(bincaslow[2:]):
        if count == 7:
            totalenabled= totalenabled+ " "+"cl"+str(count+offset)+"="+cl+"\n"
        else:
            totalenabled= totalenabled+ " "+"cl"+str(count+offset)+"="+cl
        count=count+1
    for cl in reversed(bincashigh[2:]):
        if count+offset != 19:
            if count == 7:
                totalenabled= totalenabled+ " "+"cl"+str(count+offset)+"="+cl+"\n"
            else:
                totalenabled= totalenabled+ " "+"cl"+str(count+offset)+"="+cl
        count=count+1
    print(totalenabled)
    
    
def readbus(busaddr=0,address=0x50):
    data=[]
    offset=0
    count=0
    while len(data) < 256:
            #i2caddress = 0x50  # Address of first spd eeprom device
            with SMBus(busaddr) as bus:
                bus.pec = 1
                # Read a block of 16 bytes from address 80, offset 0
                block = bus.read_i2c_block_data(address, offset, 32)
                # Returned value is a list of 32 bytes
                data.extend(block)
                offset=offset+32
                #print(block)
                count= count+1
    final=[]
    visual=[]
    for test in data:
        vis = hex(test)
        printr = '0x' + vis[2:].zfill(2)
        final.append(int(printr,16))
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
    global WRITE
    global VERBOSE
    global WRITETOFILE
    global READFROMFILE
    # Define registers values from datasheet
    parser = argparse.ArgumentParser()
    parser.add_argument("--busaddress",
                        help="set i2c bus address ( 0 most of the time)")
    parser.add_argument("--dimmaddress",
                        help="set dimm address( 0x50 0x51 0x52 0x53 0x54 0x55 )")
    parser.add_argument("--writeminrastocas",
                        help="set min ras to cas time byte 20 in ns example: --writeminrastocas 10ns")
    parser.add_argument("--writeminrastocasoffset",
                        help="set min ras to cas offset byte 36 in ns exaple: --writeminrastocas -54")  
    parser.add_argument("--writetckmin",
                        help="set min cycle time tckmin byte 12 in ns example: --writetckmin 10ns")
    parser.add_argument("--writetckminoffset",
                        help="set min cycle time tckmin offset byte 34 in ns exaple: --writetckminoffset -54")                        
    parser.add_argument("--writecas",
                        help="set enabled CAS latencies in bytes 14 and 15 These bytes define which CAS Latency (CL) values are supported. The range is from CL = 4 through CL = 18 with one bit per possible CAS Latency. A 1 in a bit position means that CL is supported, a 0 in that bit position means it is not supported. Since CL = 6 is required for all DDR3 speed bins, bit 2 of SPD byte 14 is always 1.")
    parser.add_argument("--writetofile",
                        help="write spd to filename")
    parser.add_argument("--readfromfile",
                        help="Read spd from filename")                        
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="increase output verbosity")
    parser.add_argument("-w", "--write",action="store_true",
                        help="enable write")
    args = parser.parse_args()
    
    
    #enable verbose mode
    if args.verbose:
        VERBOSE=1
    else:
        VERBOSE=0

    #set i2c bus address
    if args.busaddress:
        print(args.busaddress)
        busaddress=args.busaddress
    else:
        busaddress=0
        
    # set dimm address
    if args.dimmaddress:
        print(args.dimmaddress)
        dimmaddress=args.dimmaddress
    else:
        dimmaddress=0x50

    #enable write mode
    if args.write:
        WRITE=1
    else:
        WRITE=0
    #enable write to file and define file name    
    if args.writetofile:
        WRITETOFILE=1
        writefilename=args.writetofile
    else:
        WRITETOFILE=0
    #enable read from file and define readfilename
    if args.readfromfile:
        READFROMFILE=1
        readfilename=args.readfromfile
    else:
        READFROMFILE=0        
    
    #read from file else read from bus
    if READFROMFILE:
        final=readfromfile(readfilename)
    else:
        #read from bus and store in final
        final=readbus(busaddress, dimmaddress)

    #read original crc
    
    printcurrentcrc(final)
	#show info
    showpartnumber(final)
    showCASenabled(final)

    readminrascasdelay(final)

    readtckmin(final)
    
    readmincasdelay(final)
    
    
    #print("RAS# to CAS#  delay time =  "+str(final[18])+"MBT")
    #print(hex(final[18]))
    #print("min row precharge delay time trpmin =  "+str(final[20])+"MBT")
#    print( hex(binascii.crc_hqx(bytes.fromhex(" ".join(final[:116]))),0))
    #print(final)
    if "write" in str(args):
        print("-----after edit -----")
    
    if args.writetckmin:
        final=writetckmin(final, args.writetckmin, args.writetckminoffset)  
        #print("newtckmin")
        #readtckmin(final)

    if args.writeminrastocas:
        final=writerastocas(final, args.writeminrastocas, args.writeminrastocasoffset)  
               
    
    if args.writecas:
        final=writecas(final, args.writecas)  
        print("newcas")
        showCASenabled(final)  
    final=spdcrc(final)
    printcurrentcrc(final)
    if WRITE:
        writebus(busadress,dimmaddress,final)
    if WRITETOFILE:
        
        writefile(final, writefilename)
main()
