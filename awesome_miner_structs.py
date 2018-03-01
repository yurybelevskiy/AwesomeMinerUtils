import utils
from abc import ABC,abstractmethod

class Miner(object):

	def __init__(self, json):
		self.name = json['name']
		self.host = json['hostname']
		self.pool = json['pool']
		self.temperature = json['temperature']
		self.status_info = StatusInfo(json['statusInfo'])
		self.speed_info = SpeedInfo(json['speedInfo'])
		self.coin_info = CoinInfo(json['coinInfo'])

	def is_running(self):
		return self.status_info.status_display == "Mining"

	@abstractmethod
	def get_faulty_devices(self):
		pass

	@abstractmethod
	def all_devices_running(self):
		pass

class GPUMiner(Miner):

	def __init__(self, json):
		super(GPUMiner, self).__init__(json)
		self.device_list = DeviceList(json['gpuList'])

	def get_reset_gpus(self, default_mem_clock):
		faulty_gpus = list()
		for gpu in self.device_list.devices:
			if gpu.device_info.memory_clock == default_mem_clock:
				faulty_gpus.append(gpu)
		return faulty_gpus

	def all_devices_running(self, num_devices):
		return self.device_list.get_num_devices() == num_devices

class ASICMiner(Miner):

	def __init__(self, json):
		super(ASICMiner, self).__init__(json)
		self.device_list = DeviceList(json['asicList'])

class Pangolin(GPUMiner):

	NUM_GPUS = 8
	#in MHz
	DEFAULT_MEMORY_CLOCK = 4007
	GROUP = "Pang"

	def __init__(self, json):
		super(Pangolin, self).__init__(json)

	def get_reset_gpus(self):
		return super(Pangolin, self).get_reset_gpus(Pangolin.DEFAULT_MEMORY_CLOCK)

	def all_devices_running(self):
		return super(Pangolin, self).all_devices_running(Pangolin.NUM_GPUS)

class Ferm(GPUMiner):

	NUM_GPUS = 6
	#in MHz
	DEFAULT_MEMORY_CLOCK = 3847
	GROUP = "Ferm"

	def __init__(self, json):
		super(Ferm, self).__init__(json)

	def get_reset_gpus(self):
		return super(Pangolin, self).get_reset_gpus(Ferm.DEFAULT_MEMORY_CLOCK)

	def all_devices_running(self):
		return super(Pangolin, self).all_devices_running(Ferm.NUM_GPUS)

class StatusInfo(object):

	def __init__(self, json):
		self.status_display = json['statusDisplay']
		self.extra_info = json['statusLine3']

class SpeedInfo(object):

	def __init__(self, json):
		self.hashrate = json['hashrate']
		self.hashrate_val = json['hashrateValue']
		self.avg_hashrate = json['avgHashrate']

class DeviceInfo(object):

	def __init__(self, json):
		self.device_type = json['deviceType']
		self.clock = json['gpuClock']
		self.memory_clock = json['gpuMemoryClock']
		self.fan_percent = json['fanPercent']
		self.temperature = json['temperature']

class CoinInfo(object):

	def __init__(self, json):
		self.name = json['displayName']
		self.daily_revenue = json['revenuePerDay']
		self.daily_revenue_val = json['revenuePerDayValue']

class DeviceList(object):

	def __init__(self, json):
		device_list = list()
		for device_json in json:
			device = Device(device_json)
			device_list.append(device)
		self.devices = device_list

	def get_num_devices(self):
		return len(self.devices)

class Device(object):

	def __init__(self, json):
		self.name = json['name']
		self.status_info = StatusInfo(json['statusInfo'])
		self.device_info = DeviceInfo(json['deviceInfo'])
		self.speed_info = SpeedInfo(json['speedInfo'])

class GPU(Device):

	def __init__(self, json):
		super(GPU, self).__init__(json)

class ASIC(Device):

	def __init__(self, json):
		super(ASIC, self).__init__(json)

class NotificationList(object):

	def __init__(self, json):
		notifications = list()
		for notification_json in json:
			notification = Notification(notification_json)
			notifications.append(notification)
		self.notifications = self.filter_duplicate_notifications(notifications)

	'''
	Notification is considered as a duplicate if there is another notification with same 'miner_name', 'source' and 'message' 
	'''
	def filter_duplicate_notifications(self, notifications):
		filtered_notifications = list()
		for notification in notifications:
			if not utils.contains(filtered_notifications, lambda x: x.miner_name == notification.miner_name and x.source == notification.source and x.message == notification.message):
				filtered_notifications.append(notification)
		return filtered_notifications

	def get_notifications_with_prefix(self, prefix):
		return list(filter(lambda x: x.miner_name.startswith(prefix), self.notifications))


class Notification(object):

	def __init__(self, json):
		self.miner_name = json['minerName']
		self.source = json["source"]
		self.message = json["message"]
