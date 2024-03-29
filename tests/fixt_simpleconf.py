import pytest
from pathlib import Path


@pytest.fixture
def ini_file(tmpdir):
    tmpdir = Path(str(tmpdir))
    ret = tmpdir / 'default.ini'
    ret.write_text("""[default]
a = @int:1
b = @int:2

[TEST]
a = @int:3
""")
    return ret


@pytest.fixture
def ini_file_nodefault(tmpdir):
    tmpdir = Path(str(tmpdir))
    ret = tmpdir / 'default_upper.ini'
    ret.write_text("""[TEST]
a = @int:6
""")
    return ret


@pytest.fixture
def ini_file_rc(tmpdir):
    tmpdir = Path(str(tmpdir))
    ret = tmpdir / '.pylintrc'
    ret.write_text("""[DEFAULT]
a = 7
b = 8

[TEST]
a = 9
""")
    return ret


@pytest.fixture
def ini_file_noprofile(tmpdir):
    tmpdir = Path(str(tmpdir))
    ret = tmpdir / 'noprofile.ini'
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


@pytest.fixture
def env_file(tmpdir):
    tmpdir = Path(str(tmpdir))
    ret = tmpdir / 'env.env'
    ret.write_text("""
default_a=@int:1
b=@int:2
""")
    return ret


@pytest.fixture
def yaml_file(tmpdir):
    tmpdir = Path(str(tmpdir))
    ret = tmpdir / 'simpleconf.yaml'
    ret.write_text("""default:
  a: 1
b: 2
""")
    return ret


@pytest.fixture
def json_file(tmpdir):
    tmpdir = Path(str(tmpdir))
    ret = tmpdir / 'simpleconf.json'
    ret.write_text("""{"default": {"a": 1}, "b": 2}
""")
    return ret


@pytest.fixture
def toml_file(tmpdir):
    tmpdir = Path(str(tmpdir))
    ret = tmpdir / 'simpleconf.toml'
    ret.write_text("""b = 2
[default]
a = 1
""")
    return ret


@pytest.fixture
def dict_obj():
    return {"default": {"a": 1}, "b": 2}
