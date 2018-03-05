from distutils.core import setup
import py2exe

setup(
		console=["log_offline.py"],
		options={
				"py2exe":{
					"includes":['awesome_miner_utils']
				}
		}

	)