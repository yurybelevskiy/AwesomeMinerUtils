from awesome_miner_structs import Miner, Pangolin, Ferm, ASICMiner, NotificationList
import logging
import requests
import json
from multiprocessing import Queue

logger = logging.getLogger(__name__)

'''

'''
def collect_all_devices(pc_name, awesome_miner_port):
	request_url = "http://" + str(pc_name) + ":" + str(awesome_miner_port) + "/api/miners"
	response = requests.get(request_url)
	miners = list()
	if response.status_code == 200:
		miner_groups = json.loads(response.text)['groupList']
		for miner_group in miner_groups:
			miner_list = miner_group['minerList']
			for miner_json in miner_list:
				miner = Miner(miner_json)
				miners.append(miner)
		return miners
	else:
		logger.error("Failed to connect to Awesome Miner at %s!", request_url)
		return miners

'''

'''
def collect_devices_from_groups(pc_name, awesome_miner_port, groups):
	request_url = "http://" + str(pc_name) + ":" + str(awesome_miner_port) + "/api/miners"
	response = requests.get(request_url)
	miners = list()
	if response.status_code == 200:
		miner_groups = json.loads(response.text)['groupList']
		for miner_group in miner_groups:
			for key, value in miner_group.items():
				if key == "name" and value in groups:
					miner_list = miner_group['minerList']
					for miner_json in miner_list:
						# TODO: add other device types
						if value == Pangolin.GROUP:
							miner = Pangolin(miner_json)
						elif value == Ferm.GROUP:
							miner = Ferm(miner_json)
						else:
							miner = ASIC(miner_json)
						miners.append(miner)
					return miners
		logger.error("No miner groups named \"%s\"", ",".join(groups))
	else:
		logger.error("Failed to connect to Awesome Miner at %s!", request_url)
		return miners

'''

'''
def get_device_by_ip(ip_addr, pc_name, awesome_miner_port):
	request_url = "http://" + str(pc_name) + ":" + str(awesome_miner_port) + "/api/miners"
	response = requests.get(request_url)
	if response.status_code == 200:
		miner_groups = json.loads(response.text)['groupList']
		for miner_group in miner_groups:
			miner_list = miner_group['minerList']
			for miner_json in miner_list:
				miner = Miner(miner_json)
				if miner.host == ip_addr:
					return miner
		logger.warning("Failed to find miner with IP address %s", ip_addr)
		return None
	else:
		logger.error("Failed to connect to Awesome Miner at %s!", request_url)
		return None

'''

'''
def get_device_by_name(device_name, pc_name, awesome_miner_port):
	request_url = "http://" + str(pc_name) + ":" + str(awesome_miner_port) + "/api/miners"
	response = requests.get(request_url)
	if response.status_code == 200:
		miner_groups = json.loads(response.text)['groupList']
		for miner_group in miner_groups:
			miner_list = miner_group['minerList']
			for miner_json in miner_list:
				miner = Miner(miner_json)
				if miner.name == device_name:
					return miner
		logger.warning("Failed to find miner with name %s", device_name)
		return None
	else:
		logger.error("Failed to connect to Awesome Miner at %s!", request_url)
		return None

'''

'''
def collect_notifications_data(pc_name, awesome_miner_port):
	request_url = "http://" + str(pc_name) + ":" + str(awesome_miner_port) + "/api/notifications"
	response = requests.get(request_url)
	if response.status_code == 200:
		notification_list_json = json.loads(response.text)['notificationList']
		notification_list = NotificationList(notification_list_json)
		return notification_list
	else:
		logger.error("Failed to retrieve information about notifications from AwesomeMiner")
		return list()
