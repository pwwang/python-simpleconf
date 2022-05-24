# simpleconf

Simple configuration management for python

## Installation
```shell
# released version
pip install python-simpleconf

# Install support for ini
pip install python-simpleconf[ini]

# Install support for dotenv
pip install python-simpleconf[dotenv]

# Install support for yaml
pip install python-simpleconf[yaml]

# Install support for toml
pip install python-simpleconf[toml]

# Install support for all supported formats
pip install python-simpleconf[all]
```

## Features
- Multiple formats supported
- Type casting
- Profile support
- Simple APIs

## Usage

### Loading configurations

```python
from simpleconf import Config

# Load a single file
conf = Config.load('~/xxx.ini')
# load multiple files, later files override previous ones
conf = Config.load(
   '~/xxx.ini', '~/xxx.env', '~/xxx.yaml', '~/xxx.toml',
   '~/xxx.json', 'simpleconf.osenv', {'a': 3}
)

# Load a single file with a different loader
conf = Config.load('~/xxx.ini', loader="toml")
```

### Accessing configuration values

```python
from simpleconf import Config

conf = Config.load({'a': 1, 'b': {'c': 2}})
# conf.a == 1
# conf.b.c == 2
```

### Supported formats

- `.ini/.cfg/.config` (parsed by `iniconfig`).
  - For confiurations without profiles, an ini-like configuration like must have a `default` (case-insensitive) section.
- `.env` (using `python-dotenv`). A file with environment variables.
- `.yaml/.yml` (using `pyyaml`). A file with YAML data.
- `.toml` (using `rtoml`). A file with TOML data.
- `.json` (using `json`). A file with JSON data.
- `XXX.osenv`: System environment variables with prefix `XXX_` (case-sensitive) is used.
  - `XXX_A=1` will be loaded as `conf.A = 1`.
- python dictionary.

### Profile support

#### Loading configurations

##### Loading dictionaries

```python
from simpleconf import ProfileConfig

conf = ProfileConfig.load({'default': {'a': 1})
# conf.a == 1
```

##### Loading a `.env` file

`config.env`
```env
# config.env
default_a=1
```

```python
from simpleconf import ProfileConfig

conf = ProfileConfig.load('config.env')
# conf.a == 1
```

##### Loading ini-like configuration files

```ini
# config.ini
[default]
a = 1
```

```python
from simpleconf import ProfileConfig

conf = ProfileConfig.load('config.ini')
# conf.a == 1
```

##### Loading JSON files

`config.json`
```json
{
  "default": {
    "a": 1
  }
}
```

```python
from simpleconf import ProfileConfig

conf = ProfileConfig.load('config.json')
# conf.a == 1
```

##### Loading system environment variables

```python
from os import environ
from simpleconf import ProfileConfig

environ['XXX_DEFAULT_A'] = '1'

conf = ProfileConfig.load('XXX.osenv')
# conf.a == 1
```

##### Loading TOML files

```toml
# config.toml
[default]
a = 1
```

```python
from simpleconf import ProfileConfig

conf = ProfileConfig.load('config.toml')
# conf.a == 1
```

##### Loading YAML files

```yaml
# config.yaml
default:
  a: 1
```

```python
from simpleconf import ProfileConfig

conf = ProfileConfig.load('config.yaml')
# conf.a == 1
```

#### Switching profile

```python
from simpleconf import ProfileConfig

conf = ProfileConfig.load(
   {'default': {'a': 1, 'b': 2}, 'dev': {'a': 3}, 'prod': {'a': 4}}
)
# conf.a == 1; conf.b == 2
# ProfileConfig.profiles(conf) == ['default', 'dev', 'prod']
# ProfileConfig.pool(conf) == {'default': {'a': 1, 'b': 2}, 'dev': {'a': 3}, 'prod': {'a': 4}}
# ProfileConfig.current_profile(conf) == 'default'
# ProfileConfig.base_profile(conf) == 'default'

ProfileConfig.use_profile(conf, 'dev')
# conf.a == 3; conf.b == 2
# ProfileConfig.current_profile(conf) == 'dev'
# ProfileConfig.base_profile(conf) == 'default'

# use a different base profile
ProfileConfig.use_profile(conf, 'prod', base='dev')
# conf.a == 4   # No 'b' in conf
# ProfileConfig.current_profile(conf) == 'prod'
# ProfileConfig.base_profile(conf) == 'dev'

# Copy configuration instead of inplace modification
conf2 = ProfileConfig.use_profile(conf, 'dev', copy=True)
# conf2 is not conf
# conf2.a == 3; conf2.b == 2

# Use a context manager
with ProfileConfig.use_profile(conf2, 'default'):
    conf2.a == 3
    conf2.b == 2
# conf2.a == 3; conf2.b == 2
```

### Type casting

For configuration formats with type support, including dictionary, no type casting is done by this library, except that for TOML files.

TOML does not support `None` value in python. We use `rtoml` library to parse TOML files, which dumps `None` as `"null"`. So a `null_caster` is used to cast `"null"` to `None`.

A `none_caster` is also enabled for TOML files, a pure string of `"@none"` is casted to `None`.

For other formats, following casters are supported:

#### Int caster

```python
from os import environ
from simpleconf import Config

environ['XXX_A'] = '@int:1'

conf = Config.load('XXX.osenv')
# conf.a == 1 # int
```

#### Float caster

`@float:1.0` -> `1.0`

### Bool caster

`@bool:true` -> `True`
`@bool:false` -> `False`

#### Python caster

Values are casted by `ast.literal_eval()`.

```python
"@python:1" => 1  # or
"@py:1" => 1
"@py:1.0` -> `1.0`
"@py:[1, 2, 3]" => [1, 2, 3]
```

#### JSON caster

`@json:{"a": 1}` -> `{"a": 1}`

#### TOML caster

`@toml:a = 1` -> `{"a": 1}`
