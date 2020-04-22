import os
import sys
import pytest
from simpleconf import config, Config, FormatNotSupported, NoSuchProfile, Loader


def installed(module):
    try:
        __import__(module)
        return True
    except ImportError:
        return False


pytest_plugins = ["tests.fixt_simpleconf"]


def test_ini(ini_file, ini_file_upper, ini_file_rc):
    conf = Config()
    conf._load(ini_file)
    conf._revert()
    assert conf.a == 1
    assert conf.b == 2
    conf._use('TEST')
    assert conf.a == 3
    # case-insensitive, decided by ConfigBox
    #assert conf.A == 3

    with pytest.raises(NoSuchProfile):
        conf._use('NoSuchProfile', raise_exc=True)

    conf._load(ini_file_upper)
    assert conf.a == 6
    conf._use('default')
    assert conf.a == 4
    assert conf.b == 5

    with conf._with('TEST') as confx:
        assert confx.a == 6
    assert conf.a == 4

    conf._load(ini_file_rc)
    assert conf.a == 7
    assert conf.b == 8
    conf._use('TEST')
    assert conf.a == 9

    conf._load(ini_file)
    assert conf.a == 3
    conf._use('default')
    assert conf.a == 1
    assert conf.b == 2

    conf2 = conf.copy()
    assert conf2.a == 1
    assert conf2.b == 2

    conf2._use('TEST')
    assert conf2.a == 3

    conf2._revert()
    assert conf2.a == 1

    conf2.clear()
    assert len(conf2) == 0
    assert len(conf2._protected['cached']) == 0


def test_revert():
    c = Config(a=1)
    c._revert()
    assert c.a == 1

def test_copy():
    conf = Config()
    conf._load({'default': {'a': 1, 'c': 5}, 'profile': {
               'a': 2, 'b': 3}, 'profile2': {'d': 4}})
    copied = conf.copy('profile', 'default')
    assert copied.a == 2
    assert copied.b == 3
    assert copied.c == 5
    assert conf.a == 1
    conf2 = conf.copy('profile2', 'profile')
    #assert conf2 == {'a': 2, 'b': 3, 'c': 5, 'd': 4}
    assert conf2 == {'a': 2, 'b': 3, 'd': 4}
    assert conf == {'a': 1, 'c': 5}


def test_use():
    conf = Config()
    conf._load({'default': {'a': 1, 'c': 5}, 'profile': {
               'a': 2, 'b': 3}, 'profile2': {'d': 4}})
    conf2 = conf._use('profile', 'default', copy=True)
    assert conf2 == {'a': 2, 'b': 3, 'c': 5}
    assert conf == {'a': 1, 'c': 5}
    conf._use('profile2', 'profile')
    #assert conf == {'a': 2, 'd': 4, 'b': 3, 'c': 5}
    assert conf == {'a': 2, 'd': 4, 'b': 3}
    conf._use('profile2', 'default')
    assert conf == {'a': 1, 'd': 4, 'c': 5}

    conf._use('profile', 'profile')
    #assert conf == {'a': 2, 'b': 3, 'c': 5}
    assert conf == {'a': 2, 'b': 3}

    conf._use('profile2', 'profile2')
    #assert conf == {'a': 1, 'd': 4, 'c': 5}
    assert conf == {'d': 4}
    conf._use('profile2', 'default')
    assert conf == {'a': 1, 'd': 4, 'c': 5}

    conf._use('default')
    assert conf == {'a': 1, 'c': 5}

    conf._load({'default': {'c': 6, 'e': 7}})
    conf._use('default')
    assert conf == {'a': 1, 'c': 6, 'e': 7}

    conf = Config()
    conf._load({'default': {}})
    conf._use()
    assert conf == {}
    conf._load({'default': {'id': 'p'}})
    conf._use()
    assert conf == {'id': 'p'}


def test_with():
    conf = Config()
    conf._load({'default': {'a': 1}, 'profile': {'a': 2}})
    with conf._with('profile', copy=True) as conf2:
        assert conf2.a == 2
    assert conf.a == 1


def test_ini_nosuchfile():
    conf = Config()
    conf._load('/no/such/file.ini')
    assert len(conf) == 0


def test_ini_noprofile(ini_file_noprofile):
    conf = Config(with_profile=False)
    conf._load(ini_file_noprofile)
    assert conf.a == 10
    assert conf.b == '11'
    assert conf.c == 'x:y'
    assert conf.d == 12
    assert conf.e == 13.1
    assert conf.f == True
    assert conf.g == ['a', 'b', 'c']
    assert conf.h == None
    assert conf.i == 1e-3
    assert conf.j == True
    assert conf.k == 'k'
    with pytest.raises(ValueError):
        conf._use('default')


def test_loader_load_not_implemented():
    with pytest.raises(NotImplementedError):
        Loader('', True).load('')


def test_load_exc():
    conf = Config()
    with pytest.raises(FormatNotSupported):
        conf._load('a.xyz')


@pytest.mark.skipif(not installed('dotenv'), reason='python-dotenv not installed.')
def test_envloader(env_file):
    conf = Config()
    conf._load('/no/such/a.env')
    conf._load(env_file)
    assert conf.a == 1
    with pytest.raises(AttributeError):
        assert conf.b == 2

    conf = Config(with_profile=False)
    conf._load(env_file)
    assert conf.default_a == 1
    assert conf.b == 2


def test_osenvloader():
    os.environ['PYPPL_TEST_a'] = '1'
    os.environ['PYPPL_b'] = '2'
    conf = Config()
    conf._load('PYPPL.osenv')
    conf._load('PYPPL.osenv')
    conf._use('TEST')
    assert conf.a == 1
    with pytest.raises(AttributeError):
        conf.b

    def fac(d):
        for k,v in d.items():
            d[k] = int(v)+1
        return d
    conf = Config(with_profile=False)
    conf._load('PyPPL.osenv', factory=fac)
    assert conf.TEST_a == 2
    assert conf.b == 3


@pytest.mark.skipif(not installed('yaml'), reason='pyyaml not installed.')
def test_yamlloader(yaml_file):
    conf = Config()
    conf._load('/no/such/a.yaml')
    conf._load(yaml_file)
    assert conf.a == 1
    with pytest.raises(AttributeError):
        assert conf.b == 2

    conf = Config(with_profile=False)
    conf._load(yaml_file)
    assert conf.default == {'a': 1}
    assert conf.b == 2


def test_jsonloader(json_file):
    conf = Config()
    conf._load('/no/such/a.json')
    conf._load(json_file)
    assert conf.a == 1
    with pytest.raises(AttributeError):
        assert conf.b == 2

    conf = Config(with_profile=False)
    conf._load(json_file)
    assert conf.default == {'a': 1}
    assert conf.b == 2


@pytest.mark.skipif(not installed('toml'), reason='toml not installed.')
def test_tomlloader(toml_file):
    conf = Config()
    conf._load('/no/such/a.toml')
    conf._load(toml_file)
    assert conf.a == 1
    with pytest.raises(AttributeError):
        assert conf.b == 2

    conf = Config(with_profile=False)
    conf._load(toml_file)
    assert conf.default == {'a': 1}
    assert conf.b == 2


def test_dictloader(dict_obj):
    conf = Config()
    conf._load(dict_obj)
    assert conf.a == 1
    with pytest.raises(AttributeError):
        assert conf.b == 2

    def fac(d):
        d['default']['c'] = 3
        return d
    conf = Config(with_profile=False)
    conf._load(dict_obj, factory=fac)
    assert conf.default == {'a': 1, 'c':3}
    assert conf.b == 2


def test_configloader():

    conf1 = Config()
    conf1._load({'profile1': {'a': 1, 'b': 2}})
    conf2 = Config()
    conf2._load(conf1, {'profile1': {'a': 3}})
    conf2._use('profile1')
    assert conf2.b == 2
    assert conf2.a == 3

    conf3 = Config(with_profile=False)
    conf4 = Config(with_profile=False)
    conf3._load({'a': 1, 'b': 2})
    conf4._load(conf3, {'a': 3})
    assert conf4.a == 3
    assert conf4.b == 2
