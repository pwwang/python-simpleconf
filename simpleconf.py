VERSION = '0.0.11'

import ast
import collections
from os import path
from box import ConfigBox
from collections import OrderedDict

class FormatNotSupported(Exception):
	pass

class UnknownCastType(TypeError):
	pass

class Loader(object):

	@staticmethod
	def typeCast(val):
		try:
			t, v = val.split(':', 1)
		except (AttributeError, ValueError):
			# AttributeError: 1.split, None.split
			# ValueError: t, v = 'a'.split(':', 1)
			return val
		if t == 'py':
			return ast.literal_eval(v)
		if t == 'csv':
			return str(v).split(',')
		raise UnknownCastType(t + ', currently supported: py and csv.')

	def __init__(self, cfile, with_profile):
		self.with_profile = with_profile
		self.config       = self.load(cfile)
	
	def load(self, cfile):
		pass

class IniLoader(Loader):

	def load(self, cfile):
		cfile = path.expanduser(cfile)
		if not path.isfile(cfile):
			return {}

		try:
			from ConfigParser import ConfigParser
		except ImportError:
			from configparser import ConfigParser
		except ImportError:
			raise FormatNotSupported('.ini/.cfg/.config, need ConfigParser.')
		
		config = ConfigParser()
		config.read(cfile)

		ret = {sec: dict(config.items(sec)) for sec in config.sections()}
		defaults = config.defaults() # section DEFAULT
		defaults.update(ret.get('default', {}))
		ret['default'] = defaults
		
		if not self.with_profile:
			# only default session is loaded
			return {key: Loader.typeCast(val) for key, val in defaults.items()}

		return {key: {k: Loader.typeCast(v) for k, v in val.items()} for key, val in ret.items()}

class EnvLoader(Loader):

	def load(self, cfile):

		cfile = path.expanduser(cfile)
		if not path.isfile(cfile):
			return {}

		try:
			from dotenv.main import DotEnv
		except ImportError:
			raise FormatNotSupported('.env, need python-dotenv.')
		
		# default_A = 1
		config = DotEnv(cfile).dict()
		
		if not self.with_profile:
			return {key: Loader.typeCast(val) for key, val in config.items()}
			
		ret = {}
		for key, val in config.items():
			if '_' not in key:
				continue
			profile, realkey = key.split('_', 1)
			if profile not in ret:
				ret[profile] = {realkey: Loader.typeCast(val)}
			else:
				ret[profile][realkey] = Loader.typeCast(val)
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

			if not self.with_profile:
				config[key] = Loader.typeCast(val)
				continue

			if '_' not in key:
				continue
			profile, realkey = key.split('_', 1)
			if profile not in config:
				config[profile] = {realkey: Loader.typeCast(val)}
			else:
				config[profile][realkey] = Loader.typeCast(val)
		return config

class YamlLoader(Loader):

	def load(self, cfile):
		cfile = path.expanduser(cfile)
		if not path.isfile(cfile):
			return {}

		try:
			import yaml
		except ImportError:
			raise FormatNotSupported('.yaml, need PyYAML.')

		with open(cfile) as f:
			config = yaml.load(f, Loader = yaml.BaseLoader)
		
		return config

class JsonLoader(Loader):

	def load(self, cfile):
		cfile = path.expanduser(cfile)
		if not path.isfile(cfile):
			return {}

		import json
		with open(cfile) as f:
			config = json.load(f)

		return config

class TomlLoader(Loader):

	def load(self, cfile):
		
		cfile = path.expanduser(cfile)
		if not path.isfile(cfile):
			return {}

		try:
			import toml
		except ImportError:
			raise FormatNotSupported('.toml, need toml.')

		with open(cfile) as f:
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

class NoSuchProfile(Exception):
	pass

class Config(ConfigBox):
	
	def __init__(self, *args, **kwargs):
		self.__dict__['_protected'] = dict(
			with_profile = kwargs.pop('with_profile', True),
			profile      = 'default',
			prevprofile  = None,
			cached       = OrderedDict()
		)
		super(Config, self).__init__(*args, **kwargs)

	def get(self, key, default = None, cast = None):
		ret = super(Config, self).get(key, default)
		return cast(ret) if callable(cast) else ret

	def _load(self, *names):
		cached         = self._protected['cached']
		with_profile   = self._protected['with_profile']
		profile        = self._protected['profile']
		for name in names:
			ext = 'dict' if isinstance(name, dict) else name.rpartition('.')[2]
			if ext not in Loaders:
				raise FormatNotSupported(ext)
			if ext == 'dict':
				if repr(name) not in cached:
					cached[repr(name)] = DictLoader(name, with_profile).config
				name = repr(name)
			else:
				# maybe hash the name?
				if name not in cached:
					cached[name] = Loaders[ext](name, with_profile).config
				else:
					# change the position of the configuration
					cached[name] = cached.pop(name)

			if with_profile:
				self.update(cached[name].get(profile, {}))
			else:
				self.update(cached[name])

	def copy(self, profile = None):
		ret = self.__class__(with_profile = self._protected['with_profile'], **self)
		ret._protected['profile'] = profile or self._profile
		ret._protected['cached']  = self._protected['cached']
		return ret

	def clear(self):
		super(Config, self).clear()
		self._protected['cached'] = OrderedDict()

	@property
	def _protected(self):
		return self.__dict__['_protected']

	@property
	def _profile(self):
		return self._protected['profile']

	@_profile.setter
	def _profile(self, profile):
		self._protected['profile'] = profile

	def _revert(self):
		if not self._protected['prevprofile']:
			return
		self._use(self._protected['prevprofile'])

	def _use(self, profile = 'default', raise_exc = False, copy = False):
		if not self._protected['with_profile']:
			raise ValueError('Unable to switch profile, this configuration is set without profile.')

		if profile == self._profile:
			return self.copy(profile) if copy else None

		self._protected['prevprofile'] = self._profile
		if self._profile != 'default':
			super(Config, self).clear()

		if profile != 'default':
			# load default first
			self._use()
		
		hasprofile = False
		for conf in self._protected['cached'].values():
			if profile not in conf:
				continue
			hasprofile = True
			self.update(conf[profile])
			
		if raise_exc and not hasprofile:
			raise NoSuchProfile('Config has no such profile: %s' % profile)

		self._profile = profile

		return self.copy(profile) if copy else None

config = Config()

