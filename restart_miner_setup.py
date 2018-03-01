from distutils.core import setup
import py2exe

setup(
		console=["restart_miner.py"],
		options={
				"py2exe":{
					"includes":['awesome_miner_structs', 'awesome_miner_utils'],
					"packages":['pyHS100']
				}
		}

	)