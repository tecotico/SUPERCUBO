
import argparse
import sys
import serial
import time
import logging

serialDEV = '/dev/ttyACM0'

#------------------------------
class CS100client:
    
    port='/dev/ttyACM0'
    
    def usage():
        print('Parametros minimos:')
        print('./supercubo.py -ob origen_barrido -pb paso_barrido -n num_canales -pfx prefijo_imgs -t tiempo_exp')

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
    def verifica_parametros(self, p):
        
        if p.origen_barrido == None or p.paso_barrido == None or p.ncan == None:
            usage()
            sys.exit(0) 
            
        ob = int(p.origen_barrido) 
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
            
