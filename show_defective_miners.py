import requests
import json
import sys
import logging
from awesome_miner_utils import collect_devices_from_groups, collect_notifications_data, load_config_file
from awesome_miner_structs import Pangolin, Ferm

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p', filename='show_defective_miners.log',level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
	if len(sys.argv) != 2:
		logger.error("Invalid number of arguments passed, expected 1 argument! Exiting...")
		sys.exit(0)
	# load configuration file
	config_values = load_config_file(sys.argv[1])
	if config_values is None:
		logger.error("Configuration file at %s doesn't exist or has invalid structure! Exiting...", sys.argv[1])
		sys.exit(0)
	if config_values["port"] is None:
		logger.error("Configuration file at %s doesn't contain AwesomeMiner port number! Exiting...", sys.argv[1])
		sys.exit(0)
	if config_values["pc_name"] is None:
		logger.error("Configuration file at %s doesn't contain PC name! Exiting...", sys.argv[1])
		sys.exit(0)
	# collect information about Pangolins
	gpu_miners = collect_devices_from_groups(config_values["pc_name"], int(config_values["port"]), [Pangolin.GROUP, Ferm.GROUP])
	if len(gpu_miners):
		print("********** FAULTY GPU MINERS **********")
	for gpu_miner in gpu_miners:
		if gpu_miner.is_running():
			if not gpu_miner.all_devices_running():
				print(gpu_miner.name + " has only " + str(gpu_miner.device_list.get_num_devices()) + " GPUs running")
			faulty_gpus = gpu_miner.get_reset_gpus()
			if len(faulty_gpus) > 0:
				gpu_names = list(map(lambda x: x.name, faulty_gpus))
				print(gpu_miner.name + " has GPUs " + (",".join(faulty_gpus) if len(faulty_gpus) > 1 else faulty_gpus) + " running on default memory clock")
		else:
			print(gpu_miner.name + " - " + gpu_miner.status_info.status_display)
	# collect notifications information
	notification_list = collect_notifications_data(args.pc_name[0], PORT)
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

