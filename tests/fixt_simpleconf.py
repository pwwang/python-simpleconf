import pytest


@pytest.fixture(scope="module")
def config_path(tmp_path_factory):
    # one tmp path for this module
    return tmp_path_factory.mktemp("configs")


@pytest.fixture(scope="module")
def ini_file(config_path):
    ret = config_path / 'default.ini'
    ret.write_text("""[default]
a = @int:1
b = @int:2

[TEST]
a = @int:3
""")
    return ret


@pytest.fixture(scope="module")
def ini_file_nodefault(config_path):
    ret = config_path / 'default_upper.ini'
    ret.write_text("""[TEST]
a = @int:6
""")
    return ret


@pytest.fixture(scope="module")
def ini_file_rc(config_path):
    ret = config_path / '.pylintrc'
    ret.write_text("""[DEFAULT]
a = 7
b = 8

[TEST]
a = 9
""")
    return ret


@pytest.fixture(scope="module")
def ini_file_noprofile(config_path):
    ret = config_path / 'noprofile.ini'
    ret.write_text("""[DEFAULT]
a = @py:10
b = 11
c = x:y
d = @int:12
e = @float:13.1
f = @bool:true
g = csv:a,b,c
h = @none
i = @float:1e-3
j = true
k = k
""")
    return ret


@pytest.fixture(scope="module")
def env_file(config_path):
    ret = config_path / 'env.env'
    ret.write_text("""
default_a=@int:1
b=@int:2
""")
    return ret


@pytest.fixture(scope="module")
def yaml_file(config_path):
    ret = config_path / 'simpleconf.yaml'
    ret.write_text("""default:
  a: 1
b: 2
""")
    return ret


@pytest.fixture(scope="module")
def json_file(config_path):
    ret = config_path / 'simpleconf.json'
    ret.write_text("""{"default": {"a": 1}, "b": 2}
""")
    return ret


@pytest.fixture(scope="module")
def toml_file(config_path):
    ret = config_path / 'simpleconf.toml'
    ret.write_text("""b = 2
[default]
a = 1
""")
    return ret


@pytest.fixture(scope="module")
def dict_obj():
    return {"default": {"a": 1}, "b": 2}
