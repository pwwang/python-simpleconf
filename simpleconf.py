"""Simple configuration management with python"""
__version__ = "0.4.0"
import re
import ast
import hashlib
from pathlib import Path
from collections import OrderedDict
from contextlib import contextmanager
from diot import Diot


class FormatNotSupported(Exception):
    """Raised if format not supported"""


class NoSuchProfile(Exception):
    """Raises when configuration profile does not exist"""


class Loader:
    """Abstract loader class"""
    @staticmethod
    def type_cast(val):
        """Cast type with type prefix"""
        # pylint: disable=too-many-return-statements
        if ':' in val:
            datatype, dataval = val.split(':', 1)
            if datatype not in ('int', 'float', 'bool', 'str', 'py', 'repr',
                                'csv', 'list'):
                datatype, dataval = 'str', val
            if datatype == 'int':
                return int(dataval)
            if datatype == 'float':
                return float(dataval)
            if datatype == 'bool':
                return dataval in ('True', 'TRUE', 'true', '1')
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
        if val in ('True', 'TRUE', 'true', '1', 'False', 'FALSE', 'false', '0',
                   'None', 'none'):
            return Loader.type_cast('bool:%s' % val)
        return val

    def __init__(self, cfile, with_profile):
        self.with_profile = with_profile
        self.conf = self.load(cfile)

    def load(self, cfile):
        """Defines how the configuration file should be loaded"""
        raise NotImplementedError()


class IniLoader(Loader):
    """INI loader"""
    def load(self, cfile):
        """How to load ini file"""
        cfile = Path(cfile).expanduser()
        if not cfile.is_file():
            return {}

        from configparser import ConfigParser

        conf = ConfigParser()
        conf.optionxform = str  # make it case-sensitive
        conf.read(cfile)

        ret = {sec: dict(conf.items(sec)) for sec in conf.sections()}
        defaults = conf.defaults()  # section DEFAULT
        defaults.update(ret.get('default', {}))
        ret['default'] = defaults

        if not self.with_profile:
            # only default session is loaded
            return {key: Loader.type_cast(val) for key, val in defaults.items()}

        return {
            key: {k: Loader.type_cast(v)
                  for k, v in val.items()}
            for key, val in ret.items()
        }


class EnvLoader(Loader):
    """Env file loader"""
    def load(self, cfile):

        cfile = Path(cfile).expanduser()
        if not cfile.is_file():
            return {}

        try:
            from dotenv.main import DotEnv
        except ImportError:  # pragma: no cover
            raise FormatNotSupported('.env, need python-dotenv.')

        # default_A = 1
        conf = DotEnv(cfile).dict()

        if not self.with_profile:
            return {key: Loader.type_cast(val) for key, val in conf.items()}

        ret = {}
        for key, val in conf.items():
            if '_' not in key:
                continue
            profile, realkey = key.split('_', 1)
            ret.setdefault(profile, {}).update({realkey: Loader.type_cast(val)})
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

            if not self.with_profile:
                conf[key] = Loader.type_cast(val)
                continue

            if '_' not in key:
                continue
            profile, realkey = key.split('_', 1)
            conf.setdefault(profile,
                            {}).update({realkey: Loader.type_cast(val)})
        return conf


class YamlLoader(Loader):
    """Yaml loader"""
    def load(self, cfile):
        cfile = Path(cfile).expanduser()
        if not cfile.is_file():
            return {}

        try:
            import yaml
        except ImportError:  # pragma: no cover
            raise FormatNotSupported('.yaml, need PyYAML.')

        with open(cfile) as fconf:
            conf = yaml.load(fconf, Loader=yaml.Loader)

        return conf


class JsonLoader(Loader):
    """Json loader"""
    def load(self, cfile):
        cfile = Path(cfile).expanduser()
        if not cfile.is_file():
            return {}

        import json
        with open(cfile) as fconf:
            conf = json.load(fconf)

        return conf


class TomlLoader(Loader):
    """Toml loader"""
    def load(self, cfile):

        cfile = Path(cfile).expanduser()
        if not cfile.is_file():
            return {}
        try:
            import toml
        except ImportError:  # pragma: no cover
            raise FormatNotSupported('.toml, need toml.')

        with open(cfile) as fconf:
            conf = toml.load(fconf)
        return conf


class DictLoader(Loader):
    """Dict loader"""
    def load(self, cfile):
        return cfile


LOADERS = dict(ini=IniLoader,
               cfg=IniLoader,
               conf=IniLoader,
               config=IniLoader,
               yml=YamlLoader,
               yaml=YamlLoader,
               json=JsonLoader,
               env=EnvLoader,
               osenv=OsEnvLoader,
               toml=TomlLoader,
               dict=DictLoader)

def _config_to_ext(conf):
    """Find the extension(flag) of the configuration"""
    if isinstance(conf, Config):
        return '/config'
    if isinstance(conf, dict):
        return 'dict'

    conf = Path(conf)
    ret = conf.suffix.lstrip('.')
    if not ret and conf.name.endswith('rc'):
        ret = 'rc'
    if ret == 'rc':
        return 'ini'
    return ret

class Config(Diot):
    """The main class"""
    def __init__(self, *args, with_profile=True, **kwargs):
        self.__dict__['_protected'] = dict(with_profile=with_profile,
                                           # current profiles
                                           profile=['default'],
                                           # previous profiles
                                           prevprofile=[],
                                           cached=OrderedDict(),
                                           profiles={'default'})
        super(Config, self).__init__(*args, **kwargs)


    def _load(self, *configs, factory=None):
        """Load configs"""
        # pylint: disable=too-many-branches
        cached, with_profile = (self._protected['cached'],
                                self._protected['with_profile'])

        for conf in configs:
            ext = _config_to_ext(conf)

            if ext == '/config':
                cached.update(conf._protected['cached'])
                for cname in conf._protected['cached']:
                    if with_profile:
                        self._protected['profiles'] = (self._profiles |
                                                       set(cached[cname]))
            elif ext == 'dict':
                rname = hashlib.sha256(str(sorted(conf.items()))
                                       .encode()).hexdigest()
                if rname not in cached:
                    cached[rname] = DictLoader(conf, with_profile).conf
                    if callable(factory):
                        cached[rname] = factory(cached[rname])
                if with_profile:
                    self._protected['profiles'] = (self._profiles |
                                                   set(cached[rname]))
            elif ext in LOADERS:
                # maybe hash the name?
                rname = hashlib.sha256(str(conf).encode()).hexdigest()
                if rname not in cached:
                    cached[rname] = LOADERS[ext](conf, with_profile).conf
                    if callable(factory):
                        cached[rname] = factory(cached[rname])
                    if with_profile:
                        self._protected['profiles'] = (self._profiles |
                                                       set(cached[rname]))
                else:
                    # change the position of the configuration
                    cached[rname] = cached.pop(rname)
            else:
                raise FormatNotSupported(ext)

        if with_profile:
            self._use(*self._protected['profile'])
        else:
            for conf in self._protected['cached'].values():
                self.update(conf)

    def copy(self, # pylint: disable=arguments-differ
             *profiles):
        """Copy the configuration
        @params:
            *profiles: profiles to use
        """
        ret = self.__class__(with_profile=self._protected['with_profile'],
                             **self)

        ret._protected['profile'] = self._profile
        ret._protected['cached'] = self._protected['cached'].copy()
        ret._protected['profiles'] = set(self._profiles)

        if self._protected['with_profile'] and profiles:
            ret._use(*profiles)
        return ret

    def clear(self):
        """Clear the configuration"""
        super().clear()
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
        self._use(*self._protected['prevprofile'])

    def _use(self,
             *profiles,
             raise_exc=False,
             copy=False):
        """Use a certain profile based on a "base" profile
        @params:
            profile (str|list): The profile to use
                - First profile will be lastly loaded for multiple profiles
        """
        if not self._protected['with_profile']:
            raise ValueError('Unable to switch profile, '
                             'this configuration is set without profile.')

        if raise_exc and not all(prof in self._profiles for prof in profiles):
            raise NoSuchProfile('Not all profiles exist: %s' % profiles)

        self._protected['prevprofile'] = self._protected['profile']
        profiles = profiles or ['default']

        if copy:  # thread-safe
            return self.copy(*profiles)

        super().clear()

        for prof in profiles[1:]:
            for conf in self._protected['cached'].values():
                self.update(conf.get(prof, {}))
        for conf in self._protected['cached'].values():
            self.update(conf.get(profiles[0], {}))

        self._protected['profile'] = profiles

        return None

    @contextmanager
    def _with(self, *profiles, raise_exc=False, copy=False):
        if copy:
            yield self._use(*profiles, raise_exc=raise_exc, copy=True)
        else:
            self._use(*profiles, raise_exc=raise_exc)
            yield self
            self._revert()

config = Config()  # pylint: disable=invalid-name
