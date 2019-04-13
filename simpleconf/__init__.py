from box import Box

class Config(Box):

	@staticmethod
	def Loader(ext):
		if ext[0] == '.':
			ext = ext[1:]
		if ext == 'ini' or ext == 'cfg' or ext == 'config':
			from .loader import IniLoader
			return IniLoader
		elif ext == 'yaml' or ext == 'yml':
			from .loader import YamlLoader
			return YamlLoader
		elif ext == 'toml':
			from .loader import TomlLoader
			return TomlLoader
		elif ext == 'json':
			from .loader import JsonLoader
			return JsonLoader
		elif ext == 'env':
			from .loader import EnvLoader
			return EnvLoader
		elif ext == 'osenv':
			from .loader import OsEnvLoader
			return OsEnvLoader
		else:
			from .loader import DictLoader
			return DictLoader
	
	def __init__(self):
		super(Config, self).__init__()
		self._profile = 'default'
		self._use()

	def _load(self, *names):
		for name in names:
			if isinstance(name, dict):
				ext = 'dict'
			else:
				ext = name.rpartition('.')[2]
			print name, ext
			Loader = Config.Loader(ext)
			self.update(Loader(name, self._profile).config)
	
	def _use(self, profile = 'default'):
		if self._profile != 'default':
			self.clear()
		self._profile = profile

config = Config()
config._load('./.env', 'SIMPLECONF.osenv')

