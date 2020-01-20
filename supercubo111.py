#!/usr/bin/env python3

# este programa es copia de supercubo110
# pero usa los archivos de clases indiclient.py
# y cs100client.py


import argparse
import sys
import time
import logging
import threading
from astropy.io import fits
import indiclient
import cs100client
        
#------------------------------
parser = argparse.ArgumentParser()

requiredNamed = parser.add_argument_group('required arguments')
# el eje de barrido usual es z
requiredNamed.add_argument('-ob', '--origen_barrido', required=True, dest='origen_barrido', help='Origen del barrido en el eje Z')
requiredNamed.add_argument('-pb', '--paso_barrido', dest='paso_barrido', help='Paso de barrido en el eje Z', required=True)
requiredNamed.add_argument('-n', '--ncan', dest='ncan', help='Numero de canales', required=True)
requiredNamed.add_argument('-pfx', '--prefix', dest='prefix', help='Prefijo para las imagenes', required=True)
requiredNamed.add_argument('-t', '--texp', dest='texp', help='Tiempo de exposision (segs)', required=True)
# los ejes x, y son para los valores de paralelismo
parser.add_argument('-x', '--origen_barrido_x', dest='origen_barrido_x', help='Origen del barrido en el eje X')
parser.add_argument('-y', '--origen_barrido_y', dest='origen_barrido_y', help='Origen del barrido en el eje Y')
parser.add_argument('-v', '--verbose', action='store_true', default=False, dest='verb', help='Despliega mensajes')
parser.add_argument('--inicializa', action='store_true', default=False, dest='init', help='Inicializa el CS100 antes del iniciar el supercubo')
parser.add_argument('--origen', action='store_true', default=False, dest='origen', help='Manda a Z=0 antes de iniciar y despues de terminar el supercubo')

p = parser.parse_args()

if p.verb:
    #logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
    logging.basicConfig(level=logging.INFO, format='linea: %(lineno)d %(message)s')

cs100 = cs100client.CS100client('/dev/ttyACM0')
cs100.verifica_parametros(p)
    
ob = int(p.origen_barrido)
pb = int(p.paso_barrido)
nc = int(p.ncan)  
pfx = p.prefix
texp = float(p.texp)

if p.init:
    cs100.iniciaCS100() 
        
'''
estas lineas se deben descomentar cuando se usa el CS100 por el 
puerto serie  /dev/ttyACM0
vc = cs100.verifica_controlCS100()
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

#------------------------------
if p.origen_barrido_x != None: 
    obx = int(p.origen_barrido_x)
    logging.info('CS100: moviendo eje X a posicion', obx)
    cs100.mover_a_posicion('x', obx)
    
if p.origen_barrido_y != None: 
    oby = int(p.origen_barrido_y)
    logging.info('CS100: moviendo eje Y a posicion', oby)
    cs100.mover_a_posicion('y', oby)

if p.origen:
    logging.info('CS100: moviendo al origen')
    cs100.mover_a_posicion('z', 0)
    
#-----------------------------
# SBIG
# el cliente se conecta al localhost, pto 7624    
indiclient=indiclient.IndiClient()
indiclient.setServer("localhost",7624)

if (not(indiclient.connectServer())):
     print('Indiserver no esta corriendo en ' + indiclient.getHost())
     sys.exit(1)

time.sleep(1)

#-----------------------------
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
    #cs100.mover_a_posicion('z', newpos)
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
  
#-----------------------------
if p.origen:
    logging.info('CS100: moviendo al origen')
    cs100.mover_a_posicion('z', 0)
