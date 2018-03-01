def contains(list, filter):
	for x in list:
		if filter(x):
			return True
	return False