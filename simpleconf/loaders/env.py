import warnings
import io
from pathlib import Path
from typing import Any, Dict
from diot import Diot

from ..utils import require_package
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
from . import Loader

dotenv = require_package("dotenv")


class EnvLoader(Loader):
    """Env file loader"""

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
        """Load the configuration from a .env file"""
        if hasattr(conf, "read"):
            content = conf.read()
            return dotenv.dotenv_values(stream=io.StringIO(content))

        if not self._exists(conf, ignore_nonexist):
            return {}

        return dotenv.main.DotEnv(conf).dict()

    def load_with_profiles(  # type: ignore[override]
        self,
        conf: Any,
        ignore_nonexist: bool = False,
    ) -> Diot:
        """Load and cast the configuration from a .env file with profiles"""
        envs = self.loading(conf, ignore_nonexist)
        out = Diot()
        for k, v in envs.items():
            if "_" not in k:
                warnings.warn(
                    f"{Path(conf).name}: No profile name found in key: {k}"
                )
                continue
            profile, key = k.split("_", 1)
            profile = profile.lower()
            out.setdefault(profile, Diot())[key] = v

        return cast(out, self.__class__.CASTERS)


class EnvsLoader(EnvLoader):
    """Env string loader"""

    def loading(self, conf: Any, ignore_nonexist: bool = False) -> Dict[str, Any]:
        """Load the configuration from a .env file"""
        return dotenv.dotenv_values(stream=io.StringIO(conf))
