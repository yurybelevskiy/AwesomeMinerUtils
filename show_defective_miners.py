import requests
import json
import argparse
import sys
from awesome_miner_utils import collect_devices_from_groups, collect_notifications_data
from awesome_miner_structs import Pangolin, Ferm

#Awesome Miner API port
PORT = 17790

def main():
	# command-line parameters parsing
	parser = argparse.ArgumentParser(description='Displays faulty GPU miners by acquiring data from AwesomeMiner instance.')
	parser.add_argument("-pc", "--pc_name", nargs=1, type=str, required=True, help='Name of PC where AwesomeMiner control software is running. Can be found at Awesome Miner: Main -> Options -> Web(Awesome Miner API). In \'API address\' field, the address has a format \'http://<pc_name>:<port_number>/api\'')
	args = parser.parse_args()
	# collect information about Pangolins
	gpu_miners = collect_devices_from_groups(args.pc_name[0], PORT, [Pangolin.GROUP, Ferm.GROUP])
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

