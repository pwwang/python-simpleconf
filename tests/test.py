import os
import unittest
import tempfile
from simpleconf import config, Config
tmpdir = tempfile.gettempdir()

class TestConf(unittest.TestCase):

	@classmethod
	def setUpClass(self):
		ini = """[DEFAULT]
a = 1
b = 2

[TEST]
a = 3
"""
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
		os.remove(self.jsonfile)
		os.remove(self.tomlfile)

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
a_2 = 2
""")
		config.clear()
		config._load(inifile)
		config._use('DEF_AULT')
		self.assertEqual(config.A_1, '1')

		# no underscore in profile name
		os.environ['SIMPLE_CONF_DEF_AULT_A_1'] = '3'
		config._load('SIMPLE_CONF.osenv')
		self.assertEqual(config.A_1, '1')
		config._use('DEF')
		self.assertEqual(config.AULT_A_1, '3')

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
		
		os.environ['SIMPLECONFNOPROFILE_B'] = '3'

		env = """A = 4"""
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
		self.assertEqual(config2.int('A'), 4)
		config2._load(self.yamlfile)
		self.assertEqual(config2.int('B'), 8)
		config2._load(self.jsonfile)
		self.assertEqual(config2.int('A'), 5)
		config2._load(self.tomlfile)
		self.assertEqual(config2.int('A'), 1)
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

config3 = Config(case_sensitive = True)
class TestCaseSensitive(unittest.TestCase):

	@classmethod
	def setUpClass(self):
		ini = """[default]
a = 1
b = 2

[TEST]
a = 3
"""
		self.inifile = os.path.join(tmpdir, 'simpleconf_casesensitive.ini')
		with open(self.inifile, 'w') as f:
			f.write(ini)
		
		os.environ['SIMPLECONFCASE_TEST_b'] = '3'

		env = """
default_a = 4
"""
		self.envfile = os.path.join(tmpdir, 'simpleconf_casesensitive.env')
		with open(self.envfile, 'w') as f:
			f.write(env)

		yaml = """default:
  b: 8
test:
  a: 9
"""
		self.yamlfile = os.path.join(tmpdir, 'simpleconf_casesensitive.yaml')
		with open(self.yamlfile, 'w') as f:
			f.write(yaml)

		json = """{
	"default": {"a": 5}
}"""
		self.jsonfile = os.path.join(tmpdir, 'simpleconf_casesensitive.json')
		with open(self.jsonfile, 'w') as f:
			f.write(json)

		self.tomlfile = os.path.join(tmpdir, 'simpleconf_casesensitive.toml')
		with open(self.tomlfile, 'w') as f:
			f.write(ini)

	@classmethod
	def tearDownClass(self):
		os.remove(self.inifile)
		os.remove(self.envfile)
		os.remove(self.jsonfile)
		os.remove(self.tomlfile)

	def test(self):
		self.assertEqual(dict(config3), {})
		config3._load(self.inifile)
		self.assertEqual(config3.a, '1')
		self.assertEqual(config3.int('a'), 1)
		self.assertEqual(config3.float('b'), 2.0)
		config3._use('TEST')
		self.assertEqual(config3.int('a'), 3)
		self.assertEqual(config3.b, '2')
		config3._load('simpleconfcase.osenv')
		self.assertEqual(config3.b, '3')
		config3._use()
		self.assertEqual(config3.b, '2')
		config3._load(self.envfile)
		self.assertEqual(config3.int('a'), 4)
		config3._load(self.yamlfile)
		self.assertEqual(config3.int('b'), 8)
		config3._load(self.jsonfile)
		self.assertEqual(config3.int('a'), 5)
		config3._load(self.tomlfile)
		self.assertEqual(config3.int('a'), 1)
		self.assertEqual(config3.float('b'), 2.0)
		config3._use('TEST')
		self.assertEqual(config3.int('a'), 3)

	def testUpperCaseDefaultIni(self):
		inifile = os.path.join(tmpdir, 'simpleconfcase.ini')
		with open(inifile, 'w') as f:
			f.write("""[DEFAULT]
a_1 = 1
a_2 = 2

[PrOfIlE]
a_1 = 3
""")
		config3._load(inifile)
		config3._use('default')
		self.assertEqual(config3.int('a_1'), 1)
		self.assertEqual(config3.int('a_2'), 2)
		config3._use('profile')
		self.assertEqual(config3.int('a_1'), 1)
		config3._use('PrOfIlE')
		self.assertEqual(config3.int('a_1'), 3)
		os.remove(inifile)

if __name__ == "__main__":
	unittest.main(verbosity = 2)