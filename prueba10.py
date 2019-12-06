#!/usr/bin/env python3

import sys
import serial
import time
import select

def iniciaCS100():
	cs100 = serial.Serial('/dev/ttyACM0', baudrate=9600, bytesize=7, parity='O', stopbits=1)
	#cs100.timeout = 0.5
	print(cs100)
	cmd = '!QT\r'
	cs100.write(cmd.encode())
	print(cmd)
	time.sleep(1)
	cmd = 'O+DNC\r'
	cs100.write(cmd.encode())
	print(cmd)
	time.sleep(1)
	cmd = 'O1\r'
	cs100.write(cmd.encode())
	print(cmd)
	time.sleep(1)
	cmd = 'O0\r'
	cs100.write(cmd.encode())
	print(cmd)
	time.sleep(1)
	
	inputs = [cs100]
	running = True
	while running:
		cmd = '?\r'
		cs100.write(cmd.encode())
		print(cmd)
	
		inputready,outputready,exceptready = select.select(inputs,[],[])
	
		for s in inputready:
			if s == cs100:
				linea = cs100.readline()
				print(linea)
				if b'Z0800' in linea:
					running = False
				time.sleep(1)
					
	cmd = 'O1\r'
	cs100.write(cmd.encode())
	print(cmd)
	time.sleep(1)
	cmd = 'O0\r'
	cs100.write(cmd.encode())
	print(cmd)
	time.sleep(1)
	
	cs100.close()
	
iniciaCS100()
	
'''	
#cs100 = serial.Serial('/dev/ttyACM0', baudrate=9600, bytesize=7, parity='O', stopbits=1)
#cs100.timeout = 0.5
#print(cs100)

cmd = 'O1\r\n'
cs100.write(cmd.encode())
print(cmd)
time.sleep(2)

cmd = 'O0\r\n'
cs100.write(cmd.encode())
print(cmd)
time.sleep(2)

# eje X
cmd = 'J000P1I1I0P0\r\n'
cs100.write(cmd.encode())
print(cmd)
time.sleep(2)

# eje Y
cmd = 'J000P1I2I0P0\r\n'
cs100.write(cmd.encode())
print(cmd)
time.sleep(2)

cmd = 'O0\r\0'
cs100.write(cmd.encode())
print(cmd)
time.sleep(2)

cmd = '?\r\n'
cs100.write(cmd.encode())
print(cmd)

inputs = [cs100]
running = True
while running:
	inputready,outputready,exceptready = select.select(inputs,[],[])
	
	for s in inputready:
		if s == cs100:
			linea = cs100.readline()
			print(linea)
			
	running = False

cs100.close()
'''
