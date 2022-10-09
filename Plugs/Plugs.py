#!/usr/bin/python
from tracemalloc import start
import tinytuya
import time
import threading
import json
import logging
import datetime
import sys
from time import sleep

d = []
DB = none

dev = open('devices.json')
devices = json.load(dev)         # returns JSON object as a dict
dev.close()

logger = logging.getLogger("Plugs")
state = True

def wait_until(time):
    Time = datetime.time(*(map(int, time.split(':'))))
    while Time > datetime.datetime.today().time(): # you can add here any additional variable to break loop if necessary
        sleep(10)# you can change 1 sec interval to any other
    return

def set_logger(logger: logging.Logger, filename):
	format = "%(asctime)s >>> %(user)-9s - %(message)s"
	logging.basicConfig(level=logging.INFO, format=format)
	filehand = logging.FileHandler(f"{filename}")
	filehand.setFormatter(logging.Formatter(format))
	logger.addHandler(filehand)

def run_logging(plug_number):
	global devices, logger, state

	while state:
		d[plug_number].updatedps([18,20]) 
		data = d[plug_number].status()

		log_str = f"{data.get('dps').get('1')}, {data.get('dps').get('20')} V, {data.get('dps').get('18') :06} mA"
		logger.info(log_str, extra = {'user':devices[plug_number].get('name')})
		time.sleep(20)
	return


def log_program():
	while True:
		i = 0
		for device in devices:
			d.append( tinytuya.OutletDevice(device.get('id'), device.get('ip'), device.get('key')))
			d[i].set_version(3.3) 
			i += 1       # Closing file
		obj = datetime.datetime.now()
		set_logger(logger, f"Plugs{obj.date()}.log")

		threads = []
		i = 0
		for device in d:
			print(i)
			threads.append( threading.Thread(target=run_logging, args=(i, )) )          
			threads[i].start()
			i += 1

		wait_until("23:59")
		state = False
		threads.clear()
		sleep(90)
		state = True

def run_main():
	global DB
	# TODO check time for booking
	# TODO if booking -> turn on -> check current every min -> start of washing -> end of washing -> notificate -> turn off
		
def main():
	# TODO connect DB -> start threads
	return



if __name__ == '__main__':
	if len (sys.argv) == 1:
		main()
	else:
		if len (sys.argv) < 2 or len (sys.argv) > 2:
			print("Unknown usage")
			sys.exit (1)

		if (sys.argv[1] == "--log" or
			sys.argv[1] == "-l"):
			log_program()
		else:
			print(f"Unknown parametr:{sys.argv[1]}")
			sys.exit (1)
