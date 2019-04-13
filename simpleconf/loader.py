
class FormatNotSupported(Exception):
	pass

class Loader(object):

	def __init__(self, cfile, profile):
		self.profile   = profile
		self.nosection = False
		self.allconfig = self.load(cfile)
		self.config    = self.select()

	def select(self):
		for key, val in self.allconfig.items():
			if key.upper() != self.profile.upper():
				continue
			return {k.upper():v for k, v in val.items()}
		if self.nosection:
			return {k.upper():v for k, v in self.allconfig.items()}
		else:
			return {}
	
	def load(self, cfile):
		pass

class IniLoader(Loader):

	def load(self, cfile):
		try:
			from ConfigParser import ConfigParser
		except ImportError:
			from configparser import ConfigParser
		except ImportError:
			raise FormatNotSupported('.ini/.cfg/.config, need ConfigParser.')
		
		config = ConfigParser()
		config.read(cfile)
		return config._sections

class EnvLoader(Loader):

	def load(self, cfile):

		try:
			from dotenv.main import DotEnv
		except ImportError:
			raise FormatNotSupported('.env, need python-dotenv.')
		
		# DEFAULT_A = 1
		config = DotEnv(cfile).dict()
		ret = {}
		for key, val in config.items():
			if '_' not in key:
				continue
			profile, realkey = key.split('_', 1)
			if profile not in ret:
				ret[profile] = {realkey: val}
			else:
				ret[profile][realkey] = val
		return ret

class OsEnvLoader(Loader):

	def load(self, cfile):

		from os import environ
		prefix = '%s_' % (cfile[:-6].upper())
		config = {}

		for key, val in environ.items():
			if not key.startswith(prefix):
				continue
			key = key[len(prefix):]
			if '_' not in key:
				continue
			profile, realkey = key.split('_', 1)
			if profile not in config:
				config[profile] = {realkey: val}
			else:
				config[profile][realkey] = val
		return config

class YamlLoader(Loader):

	def load(self, cfile):
		self.nosection = True

		try:
			import yaml
		except ImportError:
			raise FormatNotSupported('.yaml, need PyYAML.')

		with open(cfile) as f:
			config = yaml.load(f)
		
		return config

class JsonLoader(Loader):

	def load(self, cfile):
		self.nosection = True

		import json
		with open(cfile) as f:
			config = json.load(f)

		return config

class TomlLoader(Loader):

	def load(self, cfile, profile):

		try:
			import toml
		except ImportError:
			raise FormatNotSupported('.toml, need toml.')

		with open(cfile) as f:
			config = toml.load(f)
		return config

class DictLoader(Loader):

	def load(self, cfile):
		self.nosection = True
		return cfile
