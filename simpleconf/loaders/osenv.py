import warnings
from os import environ
from typing import Any, Dict

from diot import Diot

from . import Loader, NoConvertingPathMixin
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


class OsenvLoader(NoConvertingPathMixin, Loader):
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

    def loading(self, conf: Any, ignore_nonexist: bool = False) -> Dict[str, Any]:
        """Load the configuration from environment variables"""
        prefix = f"{conf[:-6]}_" if len(conf) > 6 else ""
        len_prefix = len(prefix)
        out = {}
        for k, v in environ.items():
            if k.startswith(prefix):
                out[k[len_prefix:]] = v
        return out

    async def a_loading(
        self,
        conf: Any,
        ignore_nonexist: bool = False,
    ) -> Dict[str, Any]:
        """Asynchronously load the configuration from environment variables"""
        return self.loading(conf, ignore_nonexist)

    @classmethod
    def _convert_with_profiles(  # type: ignore[override]
        cls,
        conf: Any,
        loaded: Dict[str, Any],
    ) -> Diot:
        out = Diot()
        for key, val in loaded.items():
            if "_" not in key:
                warnings.warn(f"{conf}: No profile name found in key: {key}")
                continue
            profile, key = key.split("_", 1)
            profile = profile.lower()
            out.setdefault(profile, Diot())[key] = val

        return cast(out, cls.CASTERS)
