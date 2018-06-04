from distutils.core import setup
import py2exe

setup(
		windows=["ping_plugs.py"],
		options={
				"py2exe":{
					"packages":['pyHS100']
				}
		}

	)