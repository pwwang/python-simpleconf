import warnings
import io
from pathlib import Path
from typing import Any, Awaitable, Dict
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
from . import Loader, NoConvertingPathMixin

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

    async def a_loading(self, conf, ignore_nonexist):
        """Asynchronously load the configuration from a .env file"""
        if hasattr(conf, "read"):
            content = conf.read()
            if isinstance(content, Awaitable):
                content = await content
            if isinstance(content, bytes):
                content = content.decode()
            return dotenv.dotenv_values(stream=io.StringIO(content))

        if not await self._a_exists(conf, ignore_nonexist):
            return {}

        return dotenv.main.DotEnv(conf).dict()

    @classmethod
    def _convert_with_profiles(  # type: ignore[override]
        cls,
        conf: Any,
        loaded: Dict[str, Any],
    ) -> Diot:
        out = Diot()
        for k, v in loaded.items():
            if "_" not in k:
                warnings.warn(f"{Path(conf).name}: No profile name found in key: {k}")
                continue
            profile, key = k.split("_", 1)
            profile = profile.lower()
            out.setdefault(profile, Diot())[key] = v

        return cast(out, cls.CASTERS)


class EnvsLoader(NoConvertingPathMixin, EnvLoader):
    """Env string loader"""

    def loading(self, conf: Any, ignore_nonexist: bool = False) -> Dict[str, Any]:
        """Load the configuration from a .env file"""
        return dotenv.dotenv_values(stream=io.StringIO(conf))
