#!/usr/bin/python
from tracemalloc import start
import tinytuya
import time
import threading
import json
import logging
import datetime
import sys
import requests

server_url="http://127.0.0.1:8000/"
secret = ""

d = []
DB = None
state = True
cur_state = True
devices = None

logger = logging.getLogger("Plugs")

def prepare_var():
	global devices
	dev = open('/home/pi/Desktop/Plugs/config/devices.json')
	devices = json.load(dev)         # returns JSON object as a dict
	dev.close()
	i = 0
	for device in devices:
		d.append( tinytuya.OutletDevice(device.get('id'), device.get('ip'), device.get('key')))
		d[i].set_version(3.3) 
		i += 1



def wait_until(stop_time):
    Time = datetime.time(*(map(int, stop_time.split(':'))))
    while Time > datetime.datetime.today().time(): # you can add here any additional variable to break loop if necessary
        time.sleep(10)# you can change 1 sec interval to any other
    return

def set_logger(logger: logging.Logger, filename):
	format = "%(asctime)s >>> %(user)-9s - %(message)s"
	logging.basicConfig(level=logging.INFO, format=format)
	filehand = logging.FileHandler(f"/home/pi/Desktop/Plugs/logs/{filename}")
	filehand.setFormatter(logging.Formatter(format))
	logger.addHandler(filehand)

def run_logging(plug_number):
	global devices, logger, state

	while state:
		d[plug_number].updatedps([18,20]) 
		data = d[plug_number].status()

		log_str = f"{data.get('dps').get('1')}, {data.get('dps').get('20')} V, {data.get('dps').get('18') :06} mA"
		logger.info(log_str, extra = {'user':devices[plug_number].get('name')})
		time.sleep(60)
	return


def log_program():
	prepare_var()
	
	obj = datetime.datetime.now()
	set_logger(logger, f"Plugs{obj.date()}.log")

	threads = []
	i = 0
	for device in d:
		print(i)
		threads.append( threading.Thread(target=run_logging, args=(i, )) )          
		threads[i].start()
		i += 1

	while True:
    	
		wait_until("23:59:50")
		time.sleep(12)
		
		obj = datetime.datetime.now()
		logger.removeHandler(logger.handlers[0])
		set_logger(logger, f"Plugs{obj.date()}.log")
		
LOG = 1
FIN = 0
		
def notification(number, option = FIN, text = ''):
	global logger
	if option == FIN:
		payload = {'finished': number}
		logger.info("finished " + str(number), extra = {'user':devices[number].get('name')})
	else:
		payload = {text: number}
		logger.info(str(number) + '=' + text, extra = {'user':devices[number].get('name')})
	# TODO check this if-else for working
	#requests.post(server_url+secret, data=payload)


def run_main(plug_number):
	global DB, devices, logger, state
	cur_state = False
	while True:
		d[plug_number].updatedps([18,20]) 
		data = d[plug_number].status()
		
		if (int(data.get('dps').get('18')) > 0 and cur_state == False):
			cur_state = True
			notification(plug_number, option = LOG, text = 'start_washing')
		
		if (int(data.get('dps').get('18')) == 0 and cur_state == True):
			cur_state = False
			notification(plug_number, option = LOG, text = 'end_washing')
			
		log_str = f"{data.get('dps').get('1')}, {data.get('dps').get('20')} V, {data.get('dps').get('18') :06} mA"
		logger.info(log_str, extra = {'user':devices[plug_number].get('name')})
		time.sleep(60)
	return
	
	# TODO check time for booking
	
	#        |--------------------------------------------------------------------------
	#        V                                                                         |
	# TODO check current every min -> start of washing -> end of washing -> notificate |
	# TODO if cur_state = False && check_booking = False -> turn_off
		
def main():
	# TODO connect DB -> start threads
	# TODO check for new booking
	prepare_var()
	obj = datetime.datetime.now()
	set_logger(logger, f"logs/main.log")

	threads = []
	i = 0
	for device in d:
		print(i)
		threads.append( threading.Thread(target=run_logging, args=(i, )) )          
		threads[i].start()
		i += 1
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
