#!/usr/bin/env python3

import argparse
import sys
import serial

serialDEV = '/dev/ttyACM0'

#------------------------------
def iniciaCS100():
	cs100 = serial.Serial(serialDEV, baudrate=9600, bytesize=7, parity='O', stopbits=1)
	#cs100.timeout = 0.5
	print(cs100)
	
	cmdsInit = ['N8\r\n','O1\r\n', '!QT\r\n', 'P0\r\n', 'I7000P1P0\r\n', 'I0\r\n', 'O0\r\n']
	for s in cmdsInit:
		print('<-', s.encode())
		cs100.write(s.encode())
		time.sleep(0.5)
		r = cs100.readline()
		print('->', r)

	while int(chr(r[1])) <= 2:
		cs100.write('?\r\n'.encode())
		time.sleep(0.5)
		r = cs100.readline()
		print('->', r, r[1], type(r[1]), int(chr(r[1])))

	cs100.close()
	
#------------------------------
def writeCMD(cmd):
	cs100 = serial.Serial(serialDEV, baudrate=9600, bytesize=7, parity='O', stopbits=1)
	#cs100.timeout = 0.5

	print('<-', cmd.encode())
	cs100.write(cmd.encode())
	time.sleep(0.5)
	r = cs100.readline()
	print('->', r)

	cs100.close()

#------------------------------
def writeCMD2(cmd):
	cs100 = serial.Serial(serialDEV, baudrate=9600, bytesize=7, parity='O', stopbits=1)
	#cs100.timeout = 0.5

	print('<-', cmd.encode())
	cs100.write(cmd.encode())
	time.sleep(0.5)
	r = cs100.readline()
	print('->', r)
	
	cs100.write('?\r\n'.encode())
	time.sleep(0.5)
	r = cs100.readline()
	print('->', r)

	cs100.close()

#------------------------------
def pos12bitshex(pos):
    if pos < 0:
        poshex = hex((pos + 2048) | 0x800)
    else:
        poshex = hex(pos & 0xfff)
        
    return str.upper(poshex[2:]).zfill(3)
	
    
#------------------------------
parser = argparse.ArgumentParser()

parser.add_argument('--inicializa', action="store_true", default=False, dest='init')
parser.add_argument('-x', '--ejex', dest='px')
parser.add_argument('-y', '--ejey', dest='py')
parser.add_argument('-z', '--ejez', dest='pz')
parser.add_argument('-sc', '--scan', action="store_true", default=False, dest='scan')
parser.add_argument('-w', '--wavelength', dest='wl')
parser.add_argument('-c', '--cteQG', dest='cteqg')
parser.add_argument('-sb', '--supercubo', action="store_true", default=False, dest='scubo')
parser.add_argument('-ob', '--origen_barrido', dest='origen_barrido')
parser.add_argument('-pb', '--paso_barrido', dest='paso_barrido')
parser.add_argument('-n', '--ncan', dest='ncan')


p = parser.parse_args()

'''
for pos in range(-2048, 2048):
    cmdCS100 = 'J' + pos12bitshex(pos) + 'P1I4I0P0?'
    print(pos, cmdCS100)
'''

if p.init:
	iniciaCS100()
	
if p.scan:
	print(p.scan)

if p.px != None:
    cmdCS100 = 'J' + pos12bitshex(int(p.px)) + 'P1I1I0P0?'
    print(cmdCS100) 
elif p.py != None:
    cmdCS100 = 'J' + pos12bitshex(int(p.py)) + 'P1I2I0P0?'
    print(cmdCS100)
elif p.pz != None:
    cmdCS100 = 'J' + pos12bitshex(int(p.pz)) + 'P1I4I0P0?'
    print(cmdCS100)
    

#writeCMD2(cmdCS100)

print()
