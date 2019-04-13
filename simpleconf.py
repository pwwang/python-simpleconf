VERSION = '0.0.1'

from os import path
from box import ConfigBox

class FormatNotSupported(Exception):
	pass

class Loader(object):

	@staticmethod
	def keyupper(dictval):
		return {k.upper() for k, v in dictval.items()}

	def __init__(self, cfile):
		self.config  = self.prepare(self.load(cfile))

	def prepare(self, config):
		return {key.upper(): {k.upper():v for k, v in val.items()} for key, val in config.items()}
	
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
		config.read(path.expanduser(cfile))
		ret = {sec: dict(config.items(sec)) for sec in config.sections()}
		ret['DEFAULT'] = config.defaults()
		return ret

class EnvLoader(Loader):

	def load(self, cfile):

		try:
			from dotenv.main import DotEnv
		except ImportError:
			raise FormatNotSupported('.env, need python-dotenv.')
		
		# DEFAULT_A = 1
		config = DotEnv(path.expanduser(cfile)).dict()
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

		with open(path.expanduser(cfile)) as f:
			config = yaml.load(f, Loader = yaml.BaseLoader)
		
		return config

class JsonLoader(Loader):

	def load(self, cfile):
		self.nosection = True

		import json
		with open(path.expanduser(cfile)) as f:
			config = json.load(f)

		return config

class TomlLoader(Loader):

	def load(self, cfile):

		try:
			import toml
		except ImportError:
			raise FormatNotSupported('.toml, need toml.')

		with open(path.expanduser(cfile)) as f:
			config = toml.load(f)
		return config

class DictLoader(Loader):

	def load(self, cfile):
		return cfile

Loaders = dict(
	ini    = IniLoader,
	cfg    = IniLoader,
	conf   = IniLoader,
	config = IniLoader,
	yml    = YamlLoader,
	yaml   = YamlLoader,
	json   = JsonLoader,
	env    = EnvLoader,
	osenv  = OsEnvLoader,
	toml   = TomlLoader,
	dict   = DictLoader
)

class Config(ConfigBox):
	
	def __init__(self):
		super(Config, self).__init__()
		self.__dict__['_protected'] = dict(
			profile = 'DEFAULT',
			cached  = {}
		)

	def get(self, key, default = None, cast = None):
		ret = super(Config, self).get(key, default)
		return cast(ret) if callable(cast) else ret

	def _load(self, *names):
		for name in names:
			ext = 'dict' if isinstance(name, dict) else name.rpartition('.')[2]
			if ext not in Loaders:
				raise FormatNotSupported(ext)
			if ext == 'dict':
				if repr(name) not in self._protected['cached']:
					self._protected['cached'][repr(name)] = DictLoader(name).config
				name = repr(name)
			else:
				if name not in self._protected['cached']:
					self._protected['cached'][name] = Loaders[ext](name).config
			self.update(self._protected['cached'][name].get(self._protected['profile'], {}))
	
	def _use(self, profile = 'DEFAULT'):
		profile = profile.upper()

		if profile == self._protected['profile']:
			return

		if self._protected['profile'] != 'DEFAULT':
			self.clear()

		if profile != 'DEFAULT':
			# load default first
			self._use()
		
		for conf in self._protected['cached'].values():
			self.update(conf.get(profile, {}))

		self._protected['profile'] = profile

config = Config()

