import os
import unittest
import tempfile
from simpleconf import config, Config
tmpdir = tempfile.gettempdir()

class TestConf(unittest.TestCase):

	@classmethod
	def setUpClass(self):
		ini = """[default]
a = 1
b = 2

[TEST]
a = 3
"""
		self.inifile = os.path.join(tmpdir, 'simpleconf.ini')
		with open(self.inifile, 'w') as f:
			f.write(ini)
		
		os.environ['SIMPLECONF_TEST_b'] = 'py:3'

		env = """
default_a = 4
"""
		self.envfile = os.path.join(tmpdir, 'simpleconf.env')
		with open(self.envfile, 'w') as f:
			f.write(env)

		yaml = """default:
  b: 8
TEST:
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
		os.remove(self.jsonfile)
		os.remove(self.tomlfile)

	def test(self):
		self.assertEqual(dict(config), {})
		config._load(self.inifile)
		self.assertEqual(config.a, '1')
		self.assertEqual(config.int('a'), 1)
		self.assertEqual(config.float('b'), 2.0)
		config._use('TEST')
		self.assertEqual(config.int('a'), 3)
		self.assertEqual(config.b, '2')
		config._load('simpleconf.osenv')
		self.assertEqual(config.b, 3)
		config._use()
		self.assertEqual(config.b, '2')
		config._load(self.envfile)
		# case insensitive
		self.assertEqual(config.int('a'), 4)
		config._load(self.yamlfile)
		self.assertEqual(config.int('b'), 8)
		config._load(self.jsonfile)
		self.assertEqual(config.int('a'), 5)
		config._load(self.tomlfile)
		self.assertEqual(config.int('a'), 1)
		self.assertEqual(config.float('b'), 2.0)
		config._use('TEST')
		self.assertEqual(config.int('a'), 3)

	def testLowerCaseDefaultIni(self):
		inifile = os.path.join(tmpdir, 'simpleconfdefault.ini')
		with open(inifile, 'w') as f:
			f.write("""[default]
a_1 = 1
a_2 = 2
""")
		config._load(inifile)
		config._use('default')
		self.assertEqual(config.int('A_1'), 1)
		self.assertEqual(config.int('A_2'), 2)
		os.remove(inifile)

	def testUnderscoreInEnv(self):
		inifile = os.path.join(tmpdir, 'simpleconfunderscore.ini')
		with open(inifile, 'w') as f:
			f.write("""[def_ault]
a_1 = 1
a_2 = py:False
""")
		config.clear()
		config._load(inifile)
		config._use('def_ault')
		self.assertEqual(config.a_1, '1')
		self.assertIs(config.a_2, False)

		# no underscore in profile name
		os.environ['SIMPLE_CONF_DEF_AULT_A_1'] = 'csv:3,3,5'
		config._load('SIMPLE_CONF.osenv')
		self.assertEqual(config.A_1, '1')
		config._use('DEF')
		self.assertEqual(config.AULT_A_1, ['3', '3', '5'])

config2 = Config(with_profile = False)
class TestConfWithoutProfile(unittest.TestCase):

	@classmethod
	def setUpClass(self):
		ini = """[DEFAULT]
a = 1
b = 2

"""
		tmpdir = tempfile.gettempdir()
		self.inifile = os.path.join(tmpdir, 'simpleconf_noprofile.ini')
		with open(self.inifile, 'w') as f:
			f.write(ini)
		
		os.environ['SIMPLECONFNOPROFILE_b'] = '3'

		env = """a = 4"""
		self.envfile = os.path.join(tmpdir, 'simpleconf_noprofile.env')
		with open(self.envfile, 'w') as f:
			f.write(env)

		yaml = """b: 8
a: 9
"""
		self.yamlfile = os.path.join(tmpdir, 'simpleconf_noprofile.yaml')
		with open(self.yamlfile, 'w') as f:
			f.write(yaml)

		json = """{"a": 5}"""
		self.jsonfile = os.path.join(tmpdir, 'simpleconf_noprofile.json')
		with open(self.jsonfile, 'w') as f:
			f.write(json)

		toml = """
a = 1
b = 2
"""
		self.tomlfile = os.path.join(tmpdir, 'simpleconf_noprofile.toml')
		with open(self.tomlfile, 'w') as f:
			f.write(toml)

	@classmethod
	def tearDownClass(self):
		os.remove(self.inifile)
		os.remove(self.envfile)
		os.remove(self.jsonfile)
		os.remove(self.tomlfile)

	def test(self):
		self.assertEqual(dict(config2), {})
		config2._load(self.inifile)
		self.assertEqual(config2.A, '1')
		self.assertEqual(config2.int('A'), 1)
		self.assertEqual(config2.float('B'), 2.0)
		self.assertEqual(config2.B, '2')
		config2._load('simpleconfnoprofile.osenv')
		self.assertEqual(config2.B, '3')
		config2._load(self.envfile)
		self.assertEqual(config2.int('a'), 4)
		config2._load(self.yamlfile)
		self.assertEqual(config2.int('b'), 8)
		config2._load(self.jsonfile)
		self.assertEqual(config2.int('a'), 5)
		config2._load(self.tomlfile)
		self.assertEqual(config2.int('a'), 1)
		self.assertEqual(config2.float('B'), 2.0)

	def testLowerCaseDefaultIni(self):
		inifile = os.path.join(tmpdir, 'simpleconfdefault.ini')
		with open(inifile, 'w') as f:
			f.write("""[default]
a_1 = 1
a_2 = 2
""")
		config2._load(inifile)
		self.assertEqual(config2.int('A_1'), 1)
		self.assertEqual(config2.int('A_2'), 2)
		os.remove(inifile)

	def testRevert(self):
		config3 = Config()
		config3._load(dict(
			default = dict(a = 1, b = 2),
			profile = dict(a = 3, b = 4)
		))
		self.assertEqual(config3.a, 1)
		self.assertEqual(config3.b, 2)
		config3._use('profile')
		self.assertEqual(config3.a, 3)
		self.assertEqual(config3.b, 4)
		config3._revert()
		self.assertEqual(config3.a, 1)
		self.assertEqual(config3.b, 2)

	def testWith(self):
		config4 = Config()
		config4._load(dict(
			default = dict(a = 1, b = 2),
			profile = dict(a = 3, b = 4)
		))
		self.assertEqual(config4.a, 1)
		self.assertEqual(config4.b, 2)
		with config4._with('profile') as cfg:
			self.assertEqual(config4.a, 3)
			self.assertEqual(config4.b, 4)
		self.assertEqual(config4.a, 1)
		self.assertEqual(config4.b, 2)


if __name__ == "__main__":
	unittest.main(verbosity = 2)