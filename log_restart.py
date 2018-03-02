import logging
import sys
import csv
import os.path
from awesome_miner_utils import get_device_by_ip, load_config_file

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p', filename='log_restart.log',level=logging.INFO)
logger = logging.getLogger(__name__)

def log_restart(filename, miner_name):
	if not os.path.isfile(filename):
		open(filename, "w").close()
	reader = csv.reader(open(filename, "r"), delimiter=",")
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
				sys.exit(0)
	if not miner_name_present:
		log_lines.append([miner_name, 1])
	writer = csv.writer(open(filename, "w"), delimiter=",")
	writer.writerows(log_lines)

def main():
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