import logging
import socket
import argparse
import os.path
from pyHS100 import SmartPlug, Discover
from pyHS100.smartdevice import SmartDeviceException
from pprint import pformat as pf

"""

"""

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p', filename='C:/Users/GM/Desktop/Utility_Scripts/logs/ping_plugs.log',level=logging.INFO)
logger = logging.getLogger(__name__)

def ping_plug(ip_addr):
	try:
		plug = SmartPlug(ip_addr)
		plug.get_sysinfo()
		logger.info("Plug %s is up and running!", ip_addr)
	except SmartDeviceException:
		logger.error("Failed to connect to the plug with IP %s", ip_addr)

def load_plug_addr(path):
	""" Loads a list of smart plug IP addresses from file

	Args:
		path: path to file storing the mapping from miner IP addresses to plug IP addresses

	Returns:
		a list of smart plug IP address.
		If functions fails to find or parse given file, returns empty list.

	"""
	ip_addresses = []
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
					plug_ip_addr = split_line[1].strip()
					try:
						socket.inet_aton(plug_ip_addr)
						ip_addresses.append(plug_ip_addr)
					except socket.error:
						logger.error("Incorrect IP address format: %s", plug_ip_addr)
	except:
		logger.error("Miner_Plug_Map.txt not found at %s! Exiting...", os.path.dirname(os.path.realpath(__file__)))
	logger.debug("Loaded miner to smart plug mapping has %d elements", len(ip_addresses))
	return ip_addresses

def main():
	#command-line parameters parsing
	parser = argparse.ArgumentParser(description="Sends sample command to smart plugs to keep connection alive. Should be launched periodically, as plugs tend to fall off the network.")
	parser.add_argument("-map", "--miner_plug_map", nargs=1, type=str, required=True, help="""Path to file storing mapping of IP addresses from miners to smart plugs.
		 File format is: <Miner IP> : <Plug IP>. Even though the information about miners IP addresses is useless for this script,
		 the file format is chosen to be like that because the same file is used for restart_miner.py script. \\n""")
	args = parser.parse_args()
	logger.debug("Configuration file: %s", args.miner_plug_map[0])
	#load miner plug map
	plug_addresses = load_plug_addr(args.miner_plug_map[0])
	for plug_addr in plug_addresses:
		ping_plug(plug_addr)

if __name__ == "__main__":
	main()