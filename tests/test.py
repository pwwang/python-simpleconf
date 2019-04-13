import os
import unittest
import simpleconf

class TestLoader(unittest.TestCase):

	def testIni(self):
		pass

class TestConf(unittest.TestCase):

	def testInit(self):
		os.environ['SIMPLECONF_DEFAULT_A'] = '1'
		conf = simpleconf.config
		print conf
		conf._load('SIMPLECONF.osenv')
		print conf


if __name__ == "__main__":
	unittest.main(verbosity = 2)