from pyHS100 import SmartPlug, Discover
from pyHS100.smartdevice import SmartDeviceException
from awesome_miner_structs import Miner
from awesome_miner_utils import get_device_by_ip, load_config_file
import threading
import socket
import logging
import os
import argparse

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p', filename='C:/Users/GM/Desktop/Utility_Scripts/logs/restart_miner.log',level=logging.INFO)
logger = logging.getLogger(__name__)

""" 
in seconds
"""
DELAY = 10.0

def load_miner_plug_map(path):
	""" Loads a mapping from miner IP addresses to smart plug IP addresses file

	Args:
		path: path to file storing the mapping

	Returns:
		dictionary where key is a miner IP address and corresponding value is a smart plug IP address.
		If functions fails to find or parse given file, returns empty dictionary. 

	"""
	ip_addresses = {}
	if not os.path.isfile(path):
		logger.error("File storing map to plug IP mapping at %s doesn't exist", path)
		return ip_addresses
	logger.debug("Loading miner to smart plug mapping from %s...", path)
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
	logger.debug("Loaded miner to smart plug mapping has %d elements", len(ip_addresses))
	return ip_addresses

def restart_plug(ip_addr, delay):
	""" Restarts a smart plug: powers it OFF and, then, ON

	Args:
		ip_addr: IP address of the smart plug 
		delay: the time to wait before powering plug ON after it was powered OFF  
	"""
	try:
		plug = SmartPlug(ip_addr)
		if plug.state == "ON":
			plug.turn_off()
			threading.Timer(delay, plug.turn_on).start()
		else:
			threading.Timer(delay, plug.turn_on).start()
		logger.info("Restart successful!")
	except SmartDeviceException:
		#TODO: add retrying to communicate again after timeout, if after multiple retry attempts it still failes, send email or Telegram
		logger.error("Failed to communicate with plug at IP address %s!", ip_addr)

def main():
	#command-line parameters parsing
	parser = argparse.ArgumentParser(description="If a miner goes offline, checks whether the miner is equipped with a smart plug and restarts the plug, thus, rebooting the miner.")
	parser.add_argument("-conf", "--config", nargs=1, type=str, required=True, help="""Path to AwesomeMiner .ini configuration file that 
		consists of AwesomeMiner web API port number and PC name where AwesomeMiner control software is running.""")
	parser.add_argument("-ip", "--ip_address", nargs=1, type=str, required=True, help="IP address of the machine that has turned off.")
	parser.add_argument("-map", "--miner_plug_map", nargs=1, type=str, required=True, help="""Path to file storing mapping of IP addresses from miners to smart plugs.
		 File format is: <Miner IP> : <Plug IP> \\n""")
	args = parser.parse_args()
	logger.debug("Configuration file: %s, IP address: %s", args.config[0], args.ip_address[0])
	logger.info("Attempting to restart miner at " + args.ip_address[0] + "...")
	#load configuration file
	config_values = load_config_file(args.config[0])
	if config_values is None:
		logger.error("Configuration file at %s doesn't exist or has invalid structure! Exiting...", args.config[0])
		return
	if config_values["AWESOMEMINER"] is None:
		logger.error("Configuration file at %s has no \"AWESOMEMINER\" parameter group! Exiting...", args.config[0])
		return
	port = config_values["AWESOMEMINER"]["port"]
	pc_name = config_values["AWESOMEMINER"]["pc_name"]
	if port is None:
		logger.error("Configuration file at %s doesn't contain AwesomeMiner port number! Exiting...", args.config[0])
		return
	if pc_name is None:
		logger.error("Configuration file at %s doesn't contain PC name! Exiting...", args.config[0])
		return
	miner = get_device_by_ip(args.ip_address[0], pc_name, int(port))
	logger.debug("Retrieved miner %s using IP %s", miner.name, args.ip_address[0])
	if miner is not None:
		miner_plug_map = load_miner_plug_map(args.miner_plug_map[0])
		if len(miner_plug_map) == 0:
			logger.debug("Empty miner to smart plug mapping loaded!")
		if miner.name in miner_plug_map:
			plug_ip = miner_plug_map[miner.name]
			logger.info("Restarting plug with IP %s...", plug_ip)
			restart_plug(plug_ip, DELAY)
		else:
			logger.error("Plug for %s seems not be installed! Exiting...", miner.name)
			#TODO: further handling, maybe Telegram or email
	else:
		logger.error("No miner with IP address %s is registered", args[0].ip_address)

if __name__ == "__main__":
	main()