"""Simple configuration management with python"""
import re
import ast
from os import path
from collections import OrderedDict
from contextlib import contextmanager
from box import ConfigBox

class FormatNotSupported(Exception):
	"""Raised if format not supported"""

class NoSuchProfile(Exception):
	"""Raises when configuration profile does not exist"""

class Loader:
	"""Abstract loader class"""

	@staticmethod
	def typeCast(val):
		"""Cast type with type prefix"""
		if ':' in val:
			datatype, dataval = val.split(':', 1)
			if datatype not in ('int', 'float', 'bool', 'str', 'py', 'repr', 'csv', 'list'):
				datatype, dataval = 'str', val
			if datatype == 'int':
				return int(dataval)
			if datatype == 'float':
				return float(dataval)
			if datatype == 'bool':
				return dataval in ('True' , 'TRUE' , 'true' , '1')
			if datatype in ('py', 'repr'):
				return ast.literal_eval(dataval)
			if datatype in ('csv', 'list'):
				return [i.strip() for i in dataval.split(',')]
			return dataval
		if val in ('none', 'None'):
			return None
		if val.isdigit():
			return int(val)
		if re.match(r'^[+-]?(?:\d*\.)?\d+(?:[Ee][+-]\d+)?$', val):
			return float(val)
		if val in ('True' , 'TRUE' , 'true' , '1', 'False', 'FALSE', 'false', '0', 'None', 'none'):
			return Loader.typeCast('bool:%s' % val)
		return val

	def __init__(self, cfile, with_profile):
		self.withProfile = with_profile
		self.conf        = self.load(cfile)

	def load(self, cfile):
		"""Defines how the configuration file should be loaded"""
		raise NotImplementedError()

class IniLoader(Loader):
	"""INI loader"""
	def load(self, cfile):
		"""How to load ini file"""
		cfile = path.expanduser(cfile)
		if not path.isfile(cfile):
			return {}

		from configparser import ConfigParser

		conf = ConfigParser()
		conf.optionxform = str # make it case-sensitive
		conf.read(cfile)

		ret = {sec: dict(conf.items(sec)) for sec in conf.sections()}
		defaults = conf.defaults() # section DEFAULT
		defaults.update(ret.get('default', {}))
		ret['default'] = defaults

		if not self.withProfile:
			# only default session is loaded
			return {key: Loader.typeCast(val) for key, val in defaults.items()}

		return {key: {k: Loader.typeCast(v) for k, v in val.items()} for key, val in ret.items()}

class EnvLoader(Loader):
	"""Env file loader"""
	def load(self, cfile):

		cfile = path.expanduser(cfile)
		if not path.isfile(cfile):
			return {}

		try:
			from dotenv.main import DotEnv
		except ImportError: # pragma: no cover
			raise FormatNotSupported('.env, need python-dotenv.')

		# default_A = 1
		conf = DotEnv(cfile).dict()

		if not self.withProfile:
			return {key: Loader.typeCast(val) for key, val in conf.items()}

		ret = {}
		for key, val in conf.items():
			if '_' not in key:
				continue
			profile, realkey = key.split('_', 1)
			ret.setdefault(profile, {}).update({realkey: Loader.typeCast(val)})
		return ret

class OsEnvLoader(Loader):
	"""Environment variable loader"""
	def load(self, cfile):

		from os import environ
		prefix = '%s_' % (cfile[:-6].upper())
		conf = {}

		for key, val in environ.items():
			if not key.startswith(prefix):
				continue
			key = key[len(prefix):]

			if not self.withProfile:
				conf[key] = Loader.typeCast(val)
				continue

			if '_' not in key:
				continue
			profile, realkey = key.split('_', 1)
			conf.setdefault(profile, {}).update({realkey: Loader.typeCast(val)})
		return conf

class YamlLoader(Loader):
	"""Yaml loader"""
	def load(self, cfile):
		cfile = path.expanduser(cfile)
		if not path.isfile(cfile):
			return {}

		try:
			import yaml
		except ImportError: # pragma: no cover
			raise FormatNotSupported('.yaml, need PyYAML.')

		with open(cfile) as fconf:
			conf = yaml.load(fconf, Loader = yaml.Loader)

		return conf

class JsonLoader(Loader):
	"""Json loader"""
	def load(self, cfile):
		cfile = path.expanduser(cfile)
		if not path.isfile(cfile):
			return {}

		import json
		with open(cfile) as fconf:
			conf = json.load(fconf)

		return conf

class TomlLoader(Loader):
	"""Toml loader"""
	def load(self, cfile):

		cfile = path.expanduser(cfile)
		if not path.isfile(cfile):
			return {}

		try:
			import toml
		except ImportError: # pragma: no cover
			raise FormatNotSupported('.toml, need toml.')

		with open(cfile) as fconf:
			conf = toml.load(fconf)
		return conf

class DictLoader(Loader):
	"""Dict loader"""
	def load(self, cfile):
		return cfile

LOADERS = dict(
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
	"""The main class"""
	def __init__(self, *args, **kwargs):
		self.__dict__['_protected'] = dict(
			with_profile = kwargs.pop('with_profile', True),
			profile      = 'default',
			prevprofile  = None,
			cached       = OrderedDict(),
			profiles     = set(['default'])
		)
		kwargs['box_intact_types'] = kwargs.get('box_intact_types', [list, Config])
		super(Config, self).__init__(*args, **kwargs)

	def _load(self, *names):
		cached         = self._protected['cached']
		with_profile   = self._protected['with_profile']
		profile        = self._protected['profile']
		for name in names:
			ext = 'dict' if isinstance(name, dict) else str(name).rpartition('.')[2]
			if ext.endswith('rc'):
				ext = 'ini'
			if ext not in LOADERS:
				raise FormatNotSupported(ext)
			if ext == 'dict':
				if repr(name) not in cached:
					cached[repr(name)] = DictLoader(name, with_profile).conf
				name = repr(name)
				if with_profile:
					self._protected['profiles'] = self._profiles | set(cached[name].keys())
			else:
				# maybe hash the name?
				name = str(name)
				if name not in cached:
					cached[name] = LOADERS[ext](name, with_profile).conf
					if with_profile:
						self._protected['profiles'] = self._profiles | set(cached[name].keys())
				else:
					# change the position of the configuration
					cached[name] = cached.pop(name)

			if with_profile:
				self.update(cached[name].get(profile, {}))
			else:
				self.update(cached[name])

	def copy(self, profile = None): # pylint: disable=arguments-differ
		ret = self.__class__(with_profile = self._protected['with_profile'], **self)
		ret._protected['profile']  = profile or self._profile
		ret._protected['cached']   = self._protected['cached']
		ret._protected['profiles'] = set(profile for profile in self._profiles)
		return ret

	def clear(self):
		super(Config, self).clear()
		self._protected['cached'] = OrderedDict()

	@property
	def _profiles(self):
		return self._protected['profiles']

	@property
	def _protected(self):
		return self.__dict__['_protected']

	@property
	def _profile(self):
		return self._protected['profile']

	def _revert(self):
		if not self._protected['prevprofile']:
			return
		self._use(self._protected['prevprofile'])


	def _use(self, profile = 'default', raise_exc = False, copy = False):
		if not self._protected['with_profile']:
			raise ValueError('Unable to switch profile, this configuration is set without profile.')

		if raise_exc and profile != 'default' and not any(
			profile in conf for conf in self._protected['cached'].values()):
			raise NoSuchProfile('Config has no such profile: %s' % profile)

		if profile == self._profile:
			return self.copy(profile) if copy else None

		self._protected['prevprofile'] = self._profile
		if self._profile != 'default':
			super(Config, self).clear()

		if profile != 'default':
			# load default first
			self._use()

		for conf in self._protected['cached'].values():
			self.update(conf.get(profile, {}))

		self._protected['profile'] = profile

		return self.copy(profile) if copy else None

	@contextmanager
	def _with(self, profile = 'default', raise_exc = False):
		yield self._use(profile, raise_exc, copy = True)
		self._revert()

config = Config() # pylint: disable=invalid-name
