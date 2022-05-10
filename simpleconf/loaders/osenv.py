from os import environ
from typing import Any
import warnings

from diot import Diot

from . import Loader
from ..caster import (
    cast,
    int_caster,
    float_caster,
    bool_caster,
    none_caster,
    python_caster,
    py_caster,
    json_caster,
    toml_caster,
)


class OsenvLoader(Loader):
    """Environment variable loader"""

    CASTERS = [
        int_caster,
        float_caster,
        bool_caster,
        none_caster,
        python_caster,
        py_caster,
        json_caster,
        toml_caster,
    ]

    def loading(self, conf: Any, ignore_nonexist: bool = False) -> Diot:
        """Load the configuration from environment variables"""
        prefix = f"{conf[:-6]}_" if len(conf) > 6 else ""
        len_prefix = len(prefix)
        out = Diot()
        for k, v in environ.items():
            if k.startswith(prefix):
                out[k[len_prefix :]] = v
        return out

    def load_with_profiles(
        self,
        conf: Any,
        ignore_nonexist: bool = False,
    ) -> Diot:
        prefix = f"{conf[:-6]}_" if len(conf) > 6 else ""
        len_prefix = len(prefix)
        out = Diot()
        for k, v in environ.items():
            if not k.startswith(prefix):
                continue
            key = k[len_prefix:]
            if "_" not in key:
                warnings.warn(f"{conf}: No profile name found in key: {k}")
                continue
            profile, key = key.split("_", 1)
            profile = profile.lower()
            out.setdefault(profile, Diot())[key] = v

        return cast(out, self.__class__.CASTERS)
