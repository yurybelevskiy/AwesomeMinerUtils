from distutils.core import setup
import py2exe

setup(
		windows=["restart_miner.py"],
		options={
				"py2exe":{
					"includes":['awesome_miner_structs', 'awesome_miner_utils'],
					"packages":['pyHS100']
				}
		}

	)