import tinytuya
import time
import threading
import json

d = []

def set_logger(logger: logging.Logger, filename):
	format = "%(asctime)s >>> %(user)-12s - %(message)s"
	logging.basicConfig(level=logging.INFO, format=format)
	filehand = logging.FileHandler(f"{filename}")
	filehand.setFormatter(logging.Formatter(format))
	logger.addHandler(filehand)

def run_logging(plug_number):
	logger = logging.getLogger("Plugs{plug_number}")
	set_logger(logger, f"Plugs{plug_number}.log")

	while True:
		d[plug_number].updatedps([18,20]) 
		data = d[plug_number].status()

		log_str = str(devices[plug_number].get('name')) + " -> " + str(data.get('dps').get('1')) + ", " + str(data.get('dps').get('20') / 10) +  " V, " +  str(data.get('dps').get('18')) +  " mA"
		#log_str = str(data.get('dps').get('20')) + " ; " + str(data.get('dps').get('18')) + " ; ")
		logger.info(log_str, extra = {'user':'server'})
		time.sleep(5)


def main():
	dev = open('devices.json')
	devices = json.load(dev)         # returns JSON object as a dict
	i = 0
	for device in devices:
		d.attach( tinytuya.OutletDevice(device.get('id'), device.get('ip'), device.get('key')))
		d[i].set_version(3.3) 
		i += 1

	dev.close()                   # Closing file

	threads = []
	i = 0
	for device in d:
		threads.attach( threading.Thread(target=accept_read, args=(tcp_socket_host, )) )          
		threads[i].start()
		i += 1


if __name__ == '__main__':
	main()


