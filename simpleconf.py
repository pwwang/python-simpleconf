VERSION = '0.0.9'

import collections
from os import path
from box import ConfigBox
from collections import OrderedDict

class FormatNotSupported(Exception):
	pass

class Loader(object):

	def __init__(self, cfile, with_profile, case_sensitive):
		self.with_profile   = with_profile
		self.case_sensitive = case_sensitive
		self.config         = self.prepare(self.load(cfile))

	def prepare(self, config):
		if self.case_sensitive:
			return config
		elif self.with_profile:
			return {key.upper(): {k.upper():v for k, v in val.items()} for key, val in config.items()}
		else:
			return {key.upper(): val for key, val in config.items()}
	
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
		defaults = config.defaults()
		defaults.update(ret.get('default', {}))
		ret['default'] = defaults
		
		if not self.with_profile:
			return defaults

		return ret

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
			return config
			
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

			if not self.with_profile:
				config[key] = val
				continue

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
			with_profile   = kwargs.pop('with_profile', True),
			case_sensitive = kwargs.pop('case_sensitive', False),
			profile        = 'default',
			cached         = OrderedDict()
		)
		super(Config, self).__init__(*args, **kwargs)

	def get(self, key, default = None, cast = None):
		ret = super(Config, self).get(key, default)
		return cast(ret) if callable(cast) else ret

	def _load(self, *names):
		cached         = self._protected['cached']
		with_profile   = self._protected['with_profile']
		case_sensitive = self._protected['case_sensitive']
		profile        = self._protected['profile']
		for name in names:
			ext = 'dict' if isinstance(name, dict) else name.rpartition('.')[2]
			if ext not in Loaders:
				raise FormatNotSupported(ext)
			if ext == 'dict':
				if repr(name) not in cached:
					cached[repr(name)] = DictLoader(name, with_profile, case_sensitive).config
				name = repr(name)
			else:
				# maybe hash the name?
				if name not in cached:
					cached[name] = Loaders[ext](name, with_profile, case_sensitive).config
				else:
					# change the position of the configuration
					cached[name] = cached.pop(name)

			if with_profile:
				self.update(cached[name].get(profile if case_sensitive else profile.upper(), {}))
			else:
				self.update(cached[name])

	def copy(self, profile = 'default'):
		ret = self.__class__(with_profile = self._protected['with_profile'], case_sensitive = self._protected['case_sensitive'], **self)
		ret.__dict__['_protected']['profile'] = profile
		ret.__dict__['_protected']['cached']  = self._protected['cached']
		return ret

	def clear(self):
		super(Config, self).clear()
		self._protected['cached'] = OrderedDict()

	def __getattr__(self, item):
		if self._protected['case_sensitive']:
			return super(Config, self).__getattr__(item)
		return super(Config, self).__getattr__(item.upper())

	def __getitem__(self, item, _ignore_default = False):
		if self._protected['case_sensitive']:
			return super(Config, self).__getitem__(item, _ignore_default)
		return super(Config, self).__getitem__(item.upper(), _ignore_default)
	
	def _use(self, profile = 'default', raise_exc = False):
		if not self._protected['with_profile']:
			raise ValueError('Unable to switch profile, this configuration is set without profile.')

		if not self._protected['case_sensitive']:
			profile = profile.upper()

		if profile == self._protected['profile']:
			return self.copy(profile)

		if self._protected['case_sensitive']:
			if self._protected['profile'] != 'default':
				super(Config, self).clear()
		else:
			if self._protected['profile'].upper() != 'DEFAULT':
				super(Config, self).clear()

		if self._protected['case_sensitive']:
			if profile != 'default':
				# load default first
				self._use()
		else:
			if profile != 'DEFAULT':
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

		self._protected['profile'] = profile

		return self.copy(profile)

config = Config()

