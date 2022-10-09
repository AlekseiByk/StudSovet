import tinytuya
import time
import threading
import json
import logging

d = []

dev = open('devices.json')
devices = json.load(dev)         # returns JSON object as a dict
dev.close()

logger = logging.getLogger("Plugs")

def set_logger(logger: logging.Logger, filename):
	format = "%(asctime)s >>> %(user)-12s - %(message)s"
	logging.basicConfig(level=logging.INFO, format=format)
	filehand = logging.FileHandler(f"{filename}")
	filehand.setFormatter(logging.Formatter(format))
	logger.addHandler(filehand)

def run_logging(plug_number):
	global devices, logger

	while True:
		d[plug_number].updatedps([18,20]) 
		data = d[plug_number].status()

		log_str = f"{data.get('dps').get('1')}, {data.get('dps').get('20') / 10} V, {data.get('dps').get('18') :6} mA"
		logger.info(log_str, extra = {'user':devices[plug_number].get('name')})
		time.sleep(10)


def main():

	i = 0
	for device in devices:
		d.append( tinytuya.OutletDevice(device.get('id'), device.get('ip'), device.get('key')))
		d[i].set_version(3.3) 
		i += 1       # Closing file

	set_logger(logger, f"Plugs.log")

	threads = []
	i = 0
	for device in d:
		print(i)
		threads.append( threading.Thread(target=run_logging, args=(i, )) )          
		threads[i].start()
		i += 1


if __name__ == '__main__':
	main()


