#!/usr/bin/env python3 

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
def usage():
    print('Uso:')
    print('./ejemplo3.py -ob origen_barrido -pb paso_barrido -n num_canales')

class CS100Client():
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
    def verifica_parametros(Lp):
    #[ob, pb, nc, p.origen_barrido_x, p.origen_barrido_y]
        
        if  Lp[0] < -2048 or 2047 < Lp[0]:
            print('CS100: Origen de barrido fuera de limites [-2048, 2047] en el eje Z: ', Lp[0])
            sys.exit(0)
    
        if Lp[3] != None: 
            obx = int(Lp[3])
            if  obx < -2048 or 2047 < obx:
                print('CS100: Origen de barrido fuera de limites [-2048, 2047] en el eje X: ', obx)
                sys.exit(0)

        if Lp[4] != None: 
            oby = int(Lp[4])    
            if  oby < -2048 or 2047 < oby:
                print('CS100: Origen de barrido fuera de limites [-2048, 2047] en el eje Y: ', oby)
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
    
if p.origen_barrido == None or p.paso_barrido == None or p.ncan == None:
    usage()
    sys.exit(0)
    
ob = int(p.origen_barrido)
pb = int(p.paso_barrido)
nc = int(p.ncan)  

pfx = p.prefix
texp = float(p.texp)

params = [ob, pb, nc, p.origen_barrido_x, p.origen_barrido_y]
verifica_parametros(params)

cs100client = CS100Client()
        
if p.init:
    cs100client.iniciaCS100() 
    
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

if p.origen:
    logging.info('CS100: moviendo al origen')
    cs100client.mover_a_posicion(0)

#------------------------------

if p.origen_barrido_x != None: 
    obx = int(p.origen_barrido_x)
    cs100client.mover_a_posicion('x', obx)
    
if p.origen_barrido_y != None: 
    oby = int(p.origen_barrido_y)
    cs100client.mover_a_posicion('y', oby)

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
    #cs100client.mover_a_posicion('z', newpos)
    
if p.origen:
    logging.info('CS100: moviendo al origen')
    cs100client.mover_a_posicion(0)
