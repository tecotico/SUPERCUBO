#!/usr/bin/env python3

# este programa es copia de prueba20.py
# solo hace el supercubo sobre el eje Z
# no manda posiciones a los ejex X, Y 

# este programa tiene agregado el programa
# PUMA/SBIG/INDI/cliente101.py para obtener un cuadro
# de la SBIG
# Debe estar corriendo indiserver -v indi_sbig_ccd


import argparse
import sys
import serial
import time
import logging
import PyIndi
import threading
from astropy.io import fits

serialDEV = '/dev/ttyACM0'

#------------------------------
# cliente101.py
def strISState(s):
    if (s == PyIndi.ISS_OFF):
        return "Off"
    else:
        return "On" 
  
def strIPState(s):
    if (s == PyIndi.IPS_IDLE):
        return "Idle"
    elif (s == PyIndi.IPS_OK):
        return "Ok"
    elif (s == PyIndi.IPS_BUSY):
        return "Busy"
    elif (s == PyIndi.IPS_ALERT):
        return "Alert"
  
class IndiClient(PyIndi.BaseClient):
    def __init__(self):
        super(IndiClient, self).__init__()
    def newDevice(self, d):
        pass
    def newProperty(self, p):
        pass
    def removeProperty(self, p):
        pass
    def newBLOB(self, bp):
        global blobEvent
        blobEvent.set()
        pass
    def newSwitch(self, svp):
        pass
    def newNumber(self, nvp):
        pass
    def newText(self, tvp):
        pass
    def newLight(self, lvp):
        pass
    def newMessage(self, d, m):
        pass
    def serverConnected(self):
        pass
    def serverDisconnected(self, code):
        pass

#------------------------------
def usage():
    print('Uso:')
    print('./supercubo101.py -ob origen_barrido -pb paso_barrido -n num_canales -prefix prefijo_imgs -texp tiempo_exp')

#------------------------------
def verifica_controlCS100():
    
    cs100 = serial.Serial(serialDEV, baudrate=9600, bytesize=7, parity='O', stopbits=1)
    #cs100.timeout = 0.5
    
    s = '?\r\n'
    logging.info('CS100: <- {:s}'.format(s))
    cs100.write(s.encode())
    time.sleep(0.5)
    r = cs100.readline()
    logging.info('CS100: -> {:s}'.format(r.decode()))
    
    bool1 = False
    NOR = int(chr(r[1])) & 2
    if NOR == 2:
        bool1 = True
        
    bool2 = False
    SOM = int(chr(r[1])) & 1
    if SOM == 1:
        bool2 = True

    cs100.close()
    
    # regresa una trupla (bool1, bool2)
    # bool1 = not out of range (true) out of range (false)
    # bool2 = operate (true) balance (false)
    return bool1, bool2

#------------------------------
def iniciaCS100():
    logging.info('CS100: inicializando controlador')
    cs100 = serial.Serial(serialDEV, baudrate=9600, bytesize=7, parity='O', stopbits=1)
    #cs100.timeout = 0.5
    #print(cs100)
    
    cmdsInit = ['N8\r\n','O1\r\n', '!QT\r\n', 'P0\r\n', 'I7000P1P0\r\n', 'I0\r\n', 'O0\r\n']
    for s in cmdsInit:
        logging.info('CS100: <- {:s}'.format(s))
        cs100.write(s.encode())
        time.sleep(0.5)
        r = cs100.readline()
        logging.info('CS100: -> {:s}'.format(r.decode()))

    while int(chr(r[1])) <= 2:
        logging.info('CS100: <- ?\r\n')
        cs100.write('?\r\n'.encode())
        time.sleep(0.5)
        r = cs100.readline()
        logging.info('CS100: -> {:s}'.format(r.decode()))
        
    #print('->', r)
    
    cs100.close()
    
#------------------------------
def writeCMD(cmd):
    cs100 = serial.Serial(serialDEV, baudrate=9600, bytesize=7, parity='O', stopbits=1)
    #cs100.timeout = 0.5

    logging.info('CS100: <- {:s}'.format(cmd))
    cs100.write(cmd.encode())
    time.sleep(0.5)
    r = cs100.readline()
    logging.info('CS100: -> {:s}'.format(r.decode()))

    cs100.close()
    
#------------------------------
def writeCMD2(cmd):
    cs100 = serial.Serial(serialDEV, baudrate=9600, bytesize=7, parity='O', stopbits=1)
    #cs100.timeout = 0.5

    logging.info('CS100: <- {:s}'.format(cmd))
    cs100.write(cmd.encode())
    time.sleep(0.5)
    r = cs100.readline()
    logging.info('CS100: -> {:s}'.format(r.decode()))

    cs100.close()

    return r
#------------------------------
def writeCMD3(cmd):
    cs100 = serial.Serial(serialDEV, baudrate=9600, bytesize=7, parity='O', stopbits=1)
    #cs100.timeout = 0.5

    logging.info('CS100 writeCMD3: <- {:s}'.format(cmd))
    cs100.write(cmd.encode())
    time.sleep(0.5)
    r = cs100.readline()
    logging.info('CS100: -> {:s}'.format(r.decode()))
    
    logging.info('CS100: <- ?\r\n')
    cs100.write('?\r\n'.encode())
    time.sleep(0.5)
    r = cs100.readline()
    logging.info('CS100: -> {:s}'.format(r.decode()))

    cs100.close()

#------------------------------
def pos12bitshex(pos):
    if pos < 0:
        poshex = hex((pos + 2048) | 0x800)
    else:
        poshex = hex(pos & 0xfff)
        
    return str.upper(poshex[2:]).zfill(3)
    
#------------------------------
def mover_a_posicion(np):
    cmdCS100 = 'J' + pos12bitshex(np) + 'P1I4I0P0?'
    logging.info('CS100: {:4d} - {:s}'.format(np, cmdCS100))
    r = writeCMD2(cmdCS100)
    time.sleep(0.5)
    NOR = int(chr(r[1])) & 2
    if NOR != 2:
        print('CS100: OUT OF RANGE indication')
        print('Es necesario cerrar el lazo de control (O0)')
        print('---> Origen de barrido: ', ob)
        print('---> Paso de barrido: ', pb)
        print('---> Canal: ', i)
        sys.exit(0)
    #logging.info('CS100: -> {:s}'.format(r.decode()))
    #print('mover a posicion: ', r)
    
    
#------------------------------
parser = argparse.ArgumentParser()

parser.add_argument('-ob', '--origen_barrido', dest='origen_barrido')
parser.add_argument('-pb', '--paso_barrido', dest='paso_barrido')
parser.add_argument('-n', '--ncan', dest='ncan', help='Numero de canales')
parser.add_argument('-pfx', '--prefix', dest='prefix', help='Prefijo para las imagenes')
parser.add_argument('-t', '--texp', dest='texp', help='Tiempo de exposision (segs)')
parser.add_argument('-v', '--verbose', action='store_true', default=False, dest='verb', help='Despliega mensajes')
parser.add_argument('--inicializa', action='store_true', default=False, dest='init', help='Inicializa el CS100 antes del iniciar el supercubo')
parser.add_argument('--origen', action='store_true', default=False, dest='origen', help='Manda a Z=0 antes de iniciar y despues de terminar el supercubo')

p = parser.parse_args()

if p.verb:
    #logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
    logging.basicConfig(level=logging.INFO, format='linea: %(lineno)d %(message)s')

if p.init:
    iniciaCS100()

if p.origen_barrido == None or p.paso_barrido == None or p.ncan == None:
    usage()
    sys.exit(0) 
        
'''
estas lineas se deben descomentar cuando se usa el CS100 por el 
puerto serie  /dev/ttyACM0
vc = verifica_controlCS100()
if vc[0]:
    print('CS100: Not out of range')
else:
    print('CS100: OUT OF RANGE indication')
    print('Es necesario cerrar el lazo de control (O0)')
    sys.exit(0)
if vc[1]:
    print('CS100: System in OPERATE mode')
else:
    print('CS100: System in BALANCE mode')
    print('Es necesario cambiar a modo OPERATE (O0)')
    sys.exit(0)
'''
    
ob = int(p.origen_barrido)
pb = int(p.paso_barrido)
nc = int(p.ncan)
pfx = p.prefix
texp = float(p.texp)

if  ob < -2048 or 2047 < ob:
    print('CS100: Origen de barrido fuera de limites [-2048, 2047]: ', ob)
    sys.exit(0)  

if p.origen:
    logging.info('CS100: moviendo al origen')
    mover_a_posicion(0)
    
#------------------------------
# el cliente se conecta al localhost, pto 7624    
indiclient=IndiClient()
indiclient.setServer("localhost",7624)

if (not(indiclient.connectServer())):
     print('Indiserver no esta corriendo en ' + indiclient.getHost())
     sys.exit(1)

time.sleep(1)

#ccd="CCD Simulator"
ccd='SBIG CCD'

device_ccd=indiclient.getDevice(ccd)
while not(device_ccd):
    time.sleep(0.5)
    device_ccd=indiclient.getDevice(ccd)
  
ccd_connect=device_ccd.getSwitch("CONNECTION")
while not(ccd_connect):
    time.sleep(0.5)
    ccd_connect=device_ccd.getSwitch("CONNECTION")
    
if not(device_ccd.isConnected()):
    ccd_connect[0].s=PyIndi.ISS_ON
    ccd_connect[1].s=PyIndi.ISS_OFF
    indiclient.sendNewSwitch(ccd_connect)
    
ccd_connect=device_ccd.getSwitch("CONNECTION")
while not(ccd_connect):
    time.sleep(0.5)
    ccd_connect=device_ccd.getSwitch("CONNECTION")

indiclient.setBLOBMode(PyIndi.B_ALSO, ccd, "CCD1")

ccd_ccd1=device_ccd.getBLOB("CCD1")
while not(ccd_ccd1):
    time.sleep(0.5)
    ccd_ccd1=device_ccd.getBLOB("CCD1")   
    
ccd_exposure=device_ccd.getNumber("CCD_EXPOSURE")
while not(ccd_exposure):
    time.sleep(0.5)
    ccd_exposure=device_ccd.getNumber("CCD_EXPOSURE")
    
#------------------------------

for i in range(nc):
    newpos = ob + i * pb
    if newpos < -2048 or 2047 < newpos:
        print('---> Posicion solicitada fuera de limites [-2048, 2047]: ', newpos)
        print('---> Origen de barrido: ', ob)
        print('---> Paso de barrido: ', pb)
        print('---> Canal: ', i)
        sys.exit(0)
    
    print('canal: {:2d} - pos Z: {:4d}'.format(i, newpos))
    #esta linea se deben descomentar cuando se usa el CS100
    #mover_a_posicion(newpos)
    #adquisicion SBIG
    blobEvent=threading.Event()
    blobEvent.clear()
    
    ccd_exposure[0].value = texp
    indiclient.sendNewNumber(ccd_exposure)

    blobEvent.wait()

    #print("name: ", ccd_ccd1[0].name," size: ", ccd_ccd1[0].size," format: ", ccd_ccd1[0].format)

    img=ccd_ccd1[0].getblobdata()
    filename = pfx+str(i).zfill(3)+'.fits'
    f = open(filename, 'w+b')
    f.write(img)
    f.close()
    fits.setval(filename,'ORIG_BAR',value=ob,comment='Origen del barrido')
    fits.setval(filename,'PASO_BAR',value=pb,comment='Paso de barrido')
    fits.setval(filename,'CANAL',value=i,comment='Canal actual')
    fits.setval(filename,'ZPOS',value=newpos,comment='Posicion CS100')
    print(filename)
    
    
indiclient.disconnectServer()
    
if p.origen:
    logging.info('CS100: moviendo al origen')
    mover_a_posicion(0)
