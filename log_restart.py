import logging
import sys
import csv
import os.path
from awesome_miner_utils import get_device_by_ip, load_config_file

"""
Gets executed as a result of "Detect Offline" AwesomeMiner trigger.
The purpose is to maintain statistics how often miners go offline for better understanding which miners are to be equipped with smart plugs. 
"""

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p', filename='C:/Users/User/Desktop/Utility_Scripts/logs/log_restart.log',level=logging.INFO)
logger = logging.getLogger(__name__)

def log_restart(path, miner_name):
	""" Logs miner restart in .csv file

	.csv file structure consists of 2 columns: "miner_name", "num_restarts".
	If miner is restarted, this function looks it up in the log file and, if found,
	increments value in the "num_restarts" column. If no restart attempts were logged
	for the miner, adds new row in the file indicating that the miner has once restarted.

	Args:
		filename: path to log file
		miner_name: name of the miner that restarted

	"""
	if not os.path.isfile(path):
		open(path, "w").close()
	reader = csv.reader(open(path, "r"), delimiter=",")
	log_lines = list(reader)
	# add file header if file is opened first time
	if len(log_lines)==0:
		log_lines.append(["miner_name", "restarts"])
	miner_name_present = False
	for log_line in log_lines:
		if miner_name == log_line[0]:
			miner_name_present = True
			try:
				num_restarts = int(log_line[1])
				num_restarts+=1
				log_line[1] = str(num_restarts)
			except:
				logger.error("Failed to convert %s to int! Exiting...", row[1])
				return
	if not miner_name_present:
		log_lines.append([miner_name, 1])
	writer = csv.writer(open(path, "w"), delimiter=",")
	writer.writerows(log_lines)

def main():
	#TODO: add proper description of arguments
	if len(sys.argv) != 4:
		logger.error("Invalid number of arguments passed, expected 3 arguments! Exiting...")
		sys.exit(0)
	#load configuration file
	config_values = load_config_file(sys.argv[3])
	if config_values is None:
		logger.error("Configuration file at %s doesn't exist or has invalid structure! Exiting...", sys.argv[3])
		sys.exit(0)
	if config_values["port"] is None:
		logger.error("Configuration file at %s doesn't contain AwesomeMiner port number! Exiting...", sys.argv[3])
		sys.exit(0)
	if config_values["pc_name"] is None:
		logger.error("Configuration file at %s doesn't contain PC name! Exiting...", sys.argv[3])
		sys.exit(0)
	miner = get_device_by_ip(sys.argv[2], config_values["pc_name"], int(config_values["port"]))
	if miner is not None:
		log_restart(sys.argv[1], miner.name)

if __name__ == "__main__":
	main()