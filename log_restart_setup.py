from distutils.core import setup
import py2exe

setup(
		console=["log_restart.py"],
		options={
				"py2exe":{
					"includes":['awesome_miner_utils']
				}
		}

	)