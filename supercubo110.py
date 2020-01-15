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
# ejemplo2.py
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
        self.ccd='SBIG CCD'
        self.device_ccd=self.getDevice(self.ccd)
        while not(self.device_ccd):
            time.sleep(0.5)
            self.device_ccd=self.getDevice(self.ccd)

        self.ccd_connect=self.device_ccd.getSwitch("CONNECTION")
        while not(self.ccd_connect):
            time.sleep(0.5)
            self.ccd_connect=self.device_ccd.getSwitch("CONNECTION")
    
        if not(self.device_ccd.isConnected()):
            self.ccd_connect[0].s=PyIndi.ISS_ON
            self.ccd_connect[1].s=PyIndi.ISS_OFF
            self.sendNewSwitch(self.ccd_connect)
    
        self.ccd_connect=self.device_ccd.getSwitch("CONNECTION")
        while not(self.ccd_connect):
            time.sleep(0.5)
            self.ccd_connect=self.device_ccd.getSwitch("CONNECTION")

        self.setBLOBMode(PyIndi.B_ALSO, self.ccd, "CCD1")
        
        self.ccd_ccd1=self.device_ccd.getBLOB("CCD1")
        while not(self.ccd_ccd1):
            time.sleep(0.5)
            self.ccd_ccd1=self.device_ccd.getBLOB("CCD1")   
    
        self.ccd_exposure=self.device_ccd.getNumber("CCD_EXPOSURE")
        while not(self.ccd_exposure):
            time.sleep(0.5)
            self.ccd_exposure=self.device_ccd.getNumber("CCD_EXPOSURE")   
        
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
def mover_a_posicion_orig(np):
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
def mover_a_posicion(eje, np):
    if eje == 'x':
        cmdCS100 = 'J' + pos12bitshex(np) + 'P1I1I0P0?'
    if eje == 'y':
        cmdCS100 = 'J' + pos12bitshex(np) + 'P1I2I0P0?'
    if eje == 'z':
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
    
#------------------------------
parser = argparse.ArgumentParser()

# el eje de barrido usual es z
parser.add_argument('-ob', '--origen_barrido', dest='origen_barrido', help='Origen del barrido en el eje Z')
parser.add_argument('-pb', '--paso_barrido', dest='paso_barrido', help='Paso de barrido en el eje Z')
# los ejes x, y son para los valores de paralelismo
parser.add_argument('-x', '--origen_barrido_x', dest='origen_barrido_x', help='Origen del barrido en el eje X')
parser.add_argument('-y', '--origen_barrido_y', dest='origen_barrido_y', help='Origen del barrido en el eje Y')
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
    print('CS100: Origen de barrido fuera de limites [-2048, 2047] en el eje Z: ', ob)
    sys.exit(0)
    
if p.origen_barrido_x != None: 
    obx = int(p.origen_barrido_x)
    if  obx < -2048 or 2047 < obx:
        print('CS100: Origen de barrido fuera de limites [-2048, 2047] en el eje X: ', obx)
        sys.exit(0)

if p.origen_barrido_y != None: 
    oby = int(p.origen_barrido_y)    
    if  oby < -2048 or 2047 < oby:
        print('CS100: Origen de barrido fuera de limites [-2048, 2047] en el eje Y: ', oby)
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

#------------------------------

if p.origen_barrido_x != None: 
    mover_a_posicion('x', obx)
    
if p.origen_barrido_y != None: 
    mover_a_posicion('y', oby)

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
    #mover_a_posicion('z', newpos)
    #adquisicion SBIG
    blobEvent=threading.Event()
    blobEvent.clear()
    indiclient.ccd_exposure[0].value = texp
    indiclient.sendNewNumber(indiclient.ccd_exposure)
    blobEvent.wait()
    
    img=indiclient.ccd_ccd1[0].getblobdata()
    filename = pfx+str(i).zfill(3)+'.fits'
    f = open(filename, 'w+b')
    f.write(img)
    f.close()
    fits.setval(filename,'ORIG_BAR',value=ob,comment='Origen del barrido')
    fits.setval(filename,'PASO_BAR',value=pb,comment='Paso de barrido')
    fits.setval(filename,'CANAL',value=i,comment='Canal actual')
    fits.setval(filename,'ZPOS',value=newpos,comment='Posicion CS100')
    print(filename)
    
#indiclient.disconnectServer()
    
if p.origen:
    logging.info('CS100: moviendo al origen')
    mover_a_posicion(0)
