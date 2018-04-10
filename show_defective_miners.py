import requests
import json
import argparse
import sys
import logging
from awesome_miner_utils import collect_devices_from_groups, collect_notifications_data, load_config_file
from awesome_miner_structs import Pangolin, Ferm

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p', filename='C:/Users/User/Desktop/Utility_Scripts/logs/show_defective_miners.log',level=logging.INFO)
logger = logging.getLogger(__name__)

"""
Prints list of malfunctioning GPU minersand corresponding AwesomeMiner notifications in console.
A miner is consider malfunctioning if one of the following holds:
- not all GPUs are running
- at least one GPU is running on default memory clock
- miner is offline
"""

def main():
	#command-line parameters parsing
	parser = argparse.ArgumentParser(description="Displays information about failed/malfunctioning GPU miners and shows respective notifications")
	parser.add_argument("-conf", "--config", nargs=1, type=str, required=True, help="""Path to AwesomeMiner .ini configuration file that 
		consists of AwesomeMiner web API port number and PC name where AwesomeMiner control software is running.""")
	args = parser.parse_args()
	logger.debug("Configuration file: %s", args.config[0])
	# load configuration file
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
	# collect information about Pangolins
	gpu_miners = collect_devices_from_groups(pc_name, int(port), [Pangolin.GROUP, Ferm.GROUP])
	if len(gpu_miners):
		print("********** FAULTY GPU MINERS **********")
	for gpu_miner in gpu_miners:
		if gpu_miner.is_running():
			if not gpu_miner.all_devices_running():
				print(gpu_miner.name + " has only " + str(gpu_miner.device_list.get_num_devices()) + " GPUs running")
			reset_gpus = gpu_miner.get_reset_gpus()
			if len(reset_gpus) > 0:
				gpu_names = list(map(lambda x: x.name, reset_gpus))
				print(gpu_miner.name + " has " + (",".join(gpu_names) if len(gpu_names) > 1 else gpu_names[0]) + " running on default memory clock")
		else:
			print(gpu_miner.name + " - " + gpu_miner.status_info.status_display)
	# collect notifications information
	notification_list = collect_notifications_data(pc_name, int(port))
	pang_notifications = notification_list.get_notifications_with_prefix(Pangolin.GROUP)
	ferm_notifications = notification_list.get_notifications_with_prefix(Ferm.GROUP)
	if len(pang_notifications) > 0 or len(ferm_notifications) > 0:
		print("********** NOTIFICATIONS **********")
	for pang_notification in pang_notifications:
		print(pang_notification.miner_name + ": " + pang_notification.message)
	for ferm_notification in ferm_notifications:
		print(ferm_notification.miner_name + ": " + ferm_notification.message)
	print("**********               **********")

if __name__ == "__main__":
    main()