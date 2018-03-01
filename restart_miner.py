from pyHS100 import SmartPlug, Discover
from pyHS100.smartdevice import SmartDeviceException
from awesome_miner_structs import Miner
from awesome_miner_utils import get_device_by_ip
import threading
import sys
import socket
import logging
import os

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p', filename='logs/restart_miner.log',level=logging.INFO)
logger = logging.getLogger(__name__)

#in seconds
DELAY = 10.0
#Awesome Miner API port
PORT = 17790
# PC name of the machine where mining is running at
PC_NAME = "gm-pc"

def load_plug_file(path):
	ip_addresses = {}
	try:
		with open(path) as f:
			lines = f.readlines()
			for line in lines:
				split_line = line.strip().split(":") 
				if len(split_line) != 2:
					logger.error("Failed to parse line %s", line)
				else:
					miner_name = split_line[0].strip()
					plug_ip_addr = split_line[1].strip()
					try:
						socket.inet_aton(plug_ip_addr)
						ip_addresses[miner_name] = plug_ip_addr
					except socket.error:
						logger.error("Incorrect IP address format: %s", plug_ip_addr)
	except:
		logger.error("Miner_Plug_Map.txt not found at %s! Exiting...", os.path.dirname(os.path.realpath(__file__)))
		sys.exit(0)
	return ip_addresses

def restart_plug(ip_addr):
	try:
		plug = SmartPlug(ip_addr)
		if plug.state == "ON":
			plug.turn_off()
			threading.Timer(DELAY, plug.turn_on).start()
		else:
			threading.Timer(DELAY, plug.turn_on).start()
		logger.info("Restart successful!")
	except SmartDeviceException:
		#TODO: add retrying to communicate again after timeout, if after multiple retry attempts it still failes, send email or Telegram
		logger.info("Failed to communicate with plug at IP address %s! Exiting...", ip_addr)
		sys.exit(0)

def main():
	miner_ip = sys.argv[1]
	logger.info("Attempting to restart miner at " + miner_ip + "...")
	miner = get_device_by_ip(miner_ip, PC_NAME, PORT)
	if miner is not None:
		miner_plug_map = load_plug_file("C:/Users/User/Desktop/Utility Scripts/restart_miner_executable/Miner_Plug_Map.txt")
		if miner.name in miner_plug_map:
			plug_ip = miner_plug_map[miner.name]
			logger.info("Restarting plug with IP %s...", plug_ip)
			restart_plug(plug_ip)
		else:
			logger.error("Plug for %s seems not be installed! Exiting...", miner.name)
			#TODO: further handling, maybe Telegram or email
			sys.exit(0)
	else:
		logger.error("No miner with IP address %s is registered", miner_ip)
		sys.exit(0)

if __name__ == "__main__":
	main()