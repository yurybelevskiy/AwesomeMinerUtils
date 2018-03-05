import logging
import argparse
import csv
import time
import os.path
from awesome_miner_utils import get_device_by_ip, load_config_file

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p', filename='C:/Users/User/Desktop/Utility_Scripts/logs/log_offline.log',level=logging.DEBUG)
logger = logging.getLogger(__name__)

''' AwesomeMiner built-in delay for re-executing the action, in seconds
For example, if user defined delay is 90 seconds for "Wait" action, AwesomeMiner will re-execute action in 90_96=186 seconds
'''
AM_DELAY = 96

def log_offline(path, miner_name, user_delay):
	""" Logs miner offline in .csv file

	.csv file structure consists of 2 columns: "miner_name", "num_offline".
	If miner goes offline, this function looks it up in the log file and, if found,
	increments value in the "num_offline" column. If no restart attempts were logged
	for the miner, adds new row in the file indicating that the miner has once went offline.

	Args:
		filename: path to log file
		miner_name: name of the miner that went offline
		user_delay: user-defined delay for "Wait" action in AwesomeMiner rule, in seconds

	"""
	if not os.path.isfile(path):
		logger.debug("Creating log file %s...", path)
		open(path, "w").close()
	reader = csv.reader(open(path, "r"), delimiter=",")
	log_lines = list(reader)
	logger.debug("Log lines after read: %s", str(log_lines))
	# add file header if file is opened first time
	if len(log_lines)==0:
		log_lines.append(["miner_name", "offline", "last_invoked"])
	miner_name_present = False
	for log_line in log_lines:
		if miner_name == log_line[0]:
			miner_name_present = True
			try:
				num_offline = int(log_line[1])
				last_invoked = int(log_line[2])
				now = int(time.time())
				# if delay between script invocations for this miner is less or equal than AwesomeMiner-defined delay,
				# it is likely that miner stays offline and AwesomeMiner keeps triggering it at fixed intervals of time (am_delay)  
				if (now - last_invoked) <= (user_delay + AM_DELAY + 1):
					log_line[2] = str(now)
				else:
					num_offline+=1
					log_line[1] = str(num_offline)
					log_line[2] = str(now)
			except:
				logger.error("Failed to convert %s to int! Exiting...", row[1])
				return
	if not miner_name_present:
		log_lines.append([miner_name, 1, str(int(time.time()))])
	logger.debug("Log lines before write: %s", str(log_lines))
	writer = csv.writer(open(path, "w", newline=''), delimiter=",")
	writer.writerows(log_lines)

def main():
	#command-line parameters parsing
	parser = argparse.ArgumentParser(description="Maintains .csv file with statistics how often devices registered within AwesomeMiner turn off.")
	parser.add_argument("-conf", "--config", nargs=1, type=str, required=True, help="""Path to AwesomeMiner .ini configuration file that 
		consists of AwesomeMiner web API port number and PC name where AwesomeMiner control software is running.""")
	parser.add_argument("-ip", "--ip_address", nargs=1, type=str, required=True, help="IP address of the machine that has turned off.")
	parser.add_argument("-log", "--log_file", nargs=1, type=str, required=True, help="Path to file where this script will be logging miners' offline events")
	parser.add_argument("-delay", "--user_defined_delay", nargs=1, type=int, required=True, help="""Amount of seconds that AwesomeMiner is set to wait before invoking the script again.
		Details: AwesomeMiner action associated with the \"Detect Offline\" trigger keeps getting invoked all the time while the miner stays offline.
		Therefore, this script will keep logging that the same miner is going offline, however, in reality, it went offline once and doesn't come back online. 
		To solve the issue, the proposed way is to add \"Wait\" action after \"Run Executable\" action. 
		This parameter is, actually, number of seconds to \"Wait\" so that the script can figure out that miner is just staying offline and won't log another offline attempt.""") 
	args = parser.parse_args()
	logger.debug("Configuration file: %s, IP address: %s, Log file: %s, Delay: %d", args.config[0], args.ip_address[0], args.log_file[0], args.user_defined_delay[0])
	#load configuration file
	config_values = load_config_file(args.config[0])
	logger.debug("Config values: %s", str(config_values))
	if config_values is not None:
		logger.debug("Configuration file is loaded!")
	else:
		logger.error("Configuration file failed to load!")
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
	if miner is not None:
		logger.debug("Retrieved miner %s using IP %s", miner.name, args.ip_address[0])
		log_offline(args.log_file[0], miner.name, args.user_defined_delay[0])
	else:
		logger.error("No miner with IP address %s is registered", miner_ip)

if __name__ == "__main__":
	main()