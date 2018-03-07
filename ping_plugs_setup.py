from distutils.core import setup
import py2exe

setup(
		console=["ping_plugs.py"],
		options={
				"py2exe":{
					"packages":['pyHS100']
				}
		}

	)