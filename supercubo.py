#!/usr/bin/env python3

# este programa es copia de prueba20.py
# solo hace el supercubo sobre el eje Z
# no manda posiciones a los ejex X, Y 

import argparse
import sys
import serial
import time
import logging

serialDEV = '/dev/ttyACM0'

#------------------------------
def usage():
    print('Uso:')
    print('./supercubo.py -ob origen_barrido -pb paso_barrido -n num_canales')

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
    
ob = int(p.origen_barrido)
pb = int(p.paso_barrido)
nc = int(p.ncan)
if  ob < -2048 or 2047 < ob:
    print('CS100: Origen de barrido fuera de limites [-2048, 2047]: ', ob)
    sys.exit(0)  

if p.origen:
    logging.info('CS100: moviendo al origen')
    mover_a_posicion(0)

for i in range(nc):
    newpos = ob + i * pb
    if newpos < -2048 or 2047 < newpos:
        print('---> Posicion solicitada fuera de limites [-2048, 2047]: ', newpos)
        print('---> Origen de barrido: ', ob)
        print('---> Paso de barrido: ', pb)
        print('---> Canal: ', i)
        sys.exit(0)
    
    print('canal: {:2d} - pos Z: {:4d}'.format(i, newpos))
    mover_a_posicion(newpos)
    #aqui vendria la adquisicion con la sbig
    
if p.origen:
    logging.info('CS100: moviendo al origen')
    mover_a_posicion(0)
