# simpleconf
Simple configuration management with python

## Installation
```shell
# released version
pip install python-simpleconf
# lastest version
pip install git+https://github.com/pwwang/simpleconf
```

## Features
- Simple! Simple! Simple!
- Profile switching
- Supported formats:
  - `.ini/.cfg/.config` (using `ConfigParse`)
  - `.env` (using `python-dotenv`)
  - `.yaml/.yml` (using `pyyaml`)
  - `.toml` (using `toml`)
  - `.json` (using `json`)
  - systme environment variables
  - python dictionaries
- Value casting

## Usage
### Loading configurations
```python
from simpleconf import config

# load a single file
config._load('~/xxx.ini')
# load multiple files
config._load(
   '~/xxx.ini', '~/xxx.env', '~/xxx.yaml', '~/xxx.toml',
   '~/xxx.json', 'simpleconf.osenv', {'default': {'a': 3}}
)
```

For `.env` configurations, variable name uses the profile name as prefix. For example:
```shell
default_a=1
default_b=py:1
test_a=2
```
```python
config._load('xxx.env')
config.a == '1'
config.b == 1
config._use('test')
config.a == '2'
config._revert()
config.a == '1'
```
Use `with` to temporarily switch profile:
```python
config._load('xxx.env')
config.a == '1'
config.b == 1
with config._with('test') as cfg
   config.a == '2'
config.a == '1'
```

For `.osenv` configurations, for example `simpleconf.osenv`, only variables with names start with `SIMPLECONF_` will be loaded, then the upper-cased profile name should follow.
```python
os.environ['SIMPLECONF_DEFAULT_A'] = 1
os.environ['SIMPLECONF_test_A'] = 2
config._load('simpleconf.osenv')
config.A == 1
config._use('test')
config.A == 2
```

Priority is decided by the order that configurations being loaded.
In the above example, `config.A` is `3` anyway no matter whatever value is assigned in prior configurations.

Hint: to get system environment variables always have the highest priority, they should be always loaded last.

### Switching profiles
Like `ConfigParse`, the default profile (section) will be loaded first.

```ini
[default]
a = 1
b = 2

[test]
a = 3
```

```python
config._load('xxx.ini')

config.a == 1
config.b == 2

config._use('test')
config.a == 3
config.b == 2
```

Note that `simpleconf` profiles are case-insensitive, and we use uppercase names for the first-layer configurations:
```yaml
default:
   complicated_conf:
      a = 9
```

```python
config._load('xxx.yaml')
config.complicated_conf.a == 9
```

### Getting configuration values

`simpleconf.config` is an instance of [`ConfigBox`](https://github.com/cdgriffith/Box#configbox) from `python-box`. All methods supported by `ConfigBox` is applicable with `simpleconf.config`.
Additionally, we also extended `get` method to allow user-defined `cast` method:
```python
config._load('xxx.ini')
config.int('A') == 1
config.float('A') == 1.0

def version(x):
	return '%s.0.0' % x

config.get('A', cast = version) == '1.0.0'
```

### None-profile mode
```yaml
a: 1
b: 2
```

```python
from simpleconf import Config
config = Config(with_profile = False)
config._load('xxx.yaml')
config.A == 1
config.B == 2
```

Note that in .ini configuration file, you still have to use the section name `[DEFAULT]`
