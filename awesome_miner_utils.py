from awesome_miner_structs import Miner, Pangolin, Ferm, ASICMiner, NotificationList
import logging
import requests
import json
import os.path
import configparser
from multiprocessing import Queue

"""
Helper file that contains utility functions to intetact with AwesomeMiner Web API
"""

logger = logging.getLogger(__name__)

def collect_all_devices(pc_name, awesome_miner_port):
	""" Collects all miners registered with AwesomeMiner instance

	Args:
		pc_name: name of PC where AwesomeMiner is running on	
		awesome_miner_port: port to which AwesomeMiner API listens

	Returns:
		a list of Miner instances, each representing single miner registered
		with the AwesomeMiner instance if executed successfully, otherwise, an empty list

	"""
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

def collect_devices_from_groups(pc_name, awesome_miner_port, groups):
	""" Collects all miners registered within the given AwesomeMiner group

	For example, if multiple ASIC types are registered within AwesomeMiner, each is likely to
	belong to different group i.e. "AntMiner S9" group or "AntMiner L3+" group.
	To collect only devices belonging to specific group, this function is to be used.

	Args: 
		pc_name: name of PC where AwesomeMiner is running on
		awesome_miner_port: port to which AwesomeMiner API listens
		groups: list of AwesomeMiner groups from which devices are to be collected 

	Returns:
		a list of specific Miner subclasses (based on the group)
		if executed successfully, otherwise, an empty list

	"""
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

def get_device_by_ip(ip_addr, pc_name, awesome_miner_port):
	""" Looks up information about miner using it's IP address 

	Args:
		ip_addr: an IP address of the miner to be looked up
		pc_name: name of PC where AwesomeMiner is running on
		awesome_miner_port: port to which AwesomeMiner API listens 

	Returns:
		a Miner object if executed successfully, otherwise, None 

	"""
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

def get_device_by_name(device_name, pc_name, awesome_miner_port):
	""" Looks up information about miner using it's device name

	Args:
		device name: a device name of the miner to be looked up i.e. "Pang7_7"
		pc_name: name of PC where AwesomeMiner is running on
		awesome_miner_port: port to which AwesomeMiner API listens 

	Returns:
		a Miner object if executed successfully, otherwise, None 

	"""
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

def collect_notifications_data(pc_name, awesome_miner_port):
	""" Collects all pending notifications from AwesomeMiner

	Args: 
		pc_name: name of PC where AwesomeMiner is running on
		awesome_miner_port: port to which AwesomeMiner API listens

	Returns:
		a NotificationList object if executed successfully, otherwise, None

	"""
	request_url = "http://" + str(pc_name) + ":" + str(awesome_miner_port) + "/api/notifications"
	response = requests.get(request_url)
	if response.status_code == 200:
		notification_list_json = json.loads(response.text)['notificationList']
		notification_list = NotificationList(notification_list_json)
		return notification_list
	else:
		logger.error("Failed to retrieve information about notifications from AwesomeMiner")
		return None

def load_config_file(path):
	""" Loads configuration .ini file as a dictionary of dictionaries

	Note: AwesomeMiner configuration file is expected to be in .ini format.

	Args:
		path: a path to configuration file

	Returns:
		a dictionary mapping configuration group names to dictionaries mapping parameter names to their values if executed successfully, otherwise, empty dictionary
		If file path is invalid, returns None

	"""
	config = dict()
	if not os.path.isfile(path):
		return None
	parser = configparser.ConfigParser()
	parser.read(path)
	for group_key in parser:
		group_dict = dict()
		for key in parser[group_key]:
			group_dict[key] = parser[group_key][key]
		config[group_key] = group_dict
	return config
