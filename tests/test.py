import os
import unittest
import tempfile
from simpleconf import config

class TestConf(unittest.TestCase):

	@classmethod
	def setUpClass(self):
		ini = """[DEFAULT]
a = 1
b = 2

[TEST]
a = 3
"""
		tmpdir = tempfile.gettempdir()
		self.inifile = os.path.join(tmpdir, 'simpleconf.ini')
		with open(self.inifile, 'w') as f:
			f.write(ini)
		
		os.environ['SIMPLECONF_TEST_B'] = '3'

		env = """
DEFAULT_A = 4
"""
		self.envfile = os.path.join(tmpdir, 'simpleconf.env')
		with open(self.envfile, 'w') as f:
			f.write(env)

		yaml = """default:
  b: 8
test:
  a: 9
"""
		self.yamlfile = os.path.join(tmpdir, 'simpleconf.yaml')
		with open(self.yamlfile, 'w') as f:
			f.write(yaml)

		json = """{
	"default": {"a": 5}
}"""
		self.jsonfile = os.path.join(tmpdir, 'simpleconf.json')
		with open(self.jsonfile, 'w') as f:
			f.write(json)

		self.tomlfile = os.path.join(tmpdir, 'simpleconf.toml')
		with open(self.tomlfile, 'w') as f:
			f.write(ini)

	@classmethod
	def tearDownClass(self):
		os.remove(self.inifile)
		os.remove(self.envfile)

	def test(self):
		self.assertEqual(dict(config), {})
		config._load(self.inifile)
		self.assertEqual(config.A, '1')
		self.assertEqual(config.int('A'), 1)
		self.assertEqual(config.float('B'), 2.0)
		config._use('test')
		self.assertEqual(config.int('A'), 3)
		self.assertEqual(config.B, '2')
		config._load('simpleconf.osenv')
		self.assertEqual(config.B, '3')
		config._use()
		self.assertEqual(config.B, '2')
		config._load(self.envfile)
		self.assertEqual(config.int('A'), 4)
		config._load(self.yamlfile)
		self.assertEqual(config.int('B'), 8)
		config._load(self.jsonfile)
		self.assertEqual(config.int('A'), 5)
		config._load(self.tomlfile)
		self.assertEqual(config.int('A'), 1)
		self.assertEqual(config.float('B'), 2.0)
		config._use('test')
		self.assertEqual(config.int('A'), 3)


if __name__ == "__main__":
	unittest.main(verbosity = 2)