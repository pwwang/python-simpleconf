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
from . import (
    Loader,
    NoConvertingPathMixin,
    LoaderModifierMixin,
    J2ModifierMixin,
    LiqModifierMixin,
)

dotenv = require_package("dotenv")


class EnvLoader(Loader, LoaderModifierMixin):
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
            str_content = content.decode() if isinstance(content, bytes) else content
            sio = io.StringIO(str_content)  # type: ignore[arg-type]
            return dotenv.dotenv_values(stream=sio)

        if not self._exists(conf, ignore_nonexist):
            return {}

        conf = self.__class__._convert_path(conf)
        content = conf.read_text()  # so that cloud paths work
        modified = self._modifier(content)
        str_modified = modified.decode() if isinstance(modified, bytes) else modified
        sio = io.StringIO(str_modified)  # type: ignore[arg-type]
        return dotenv.dotenv_values(stream=sio)

    async def a_loading(self, conf, ignore_nonexist):
        """Asynchronously load the configuration from a .env file"""
        if hasattr(conf, "read"):
            content = conf.read()
            if isinstance(content, Awaitable):
                content = await content
            if isinstance(content, bytes):
                content = content.decode()
            modified = self._modifier(content)
            str_modified = modified.decode() if isinstance(modified, bytes) else modified
            sio = io.StringIO(str_modified)  # type: ignore[arg-type]
            return dotenv.dotenv_values(stream=sio)

        if not await self._a_exists(conf, ignore_nonexist):
            return {}

        conf = self.__class__._convert_path(conf)
        # so that cloud paths work
        content = await conf.a_read_text()  # type: ignore[attr-defined]
        modified = self._modifier(content)
        str_modified = modified.decode() if isinstance(modified, bytes) else modified
        sio = io.StringIO(str_modified)  # type: ignore[arg-type]
        return dotenv.dotenv_values(stream=sio)

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

        return cast(out, cls.CASTERS or [])


class EnvsLoader(NoConvertingPathMixin, EnvLoader):  # type: ignore[misc]
    """Env string loader"""

    def loading(self, conf: Any, ignore_nonexist: bool = False) -> Dict[str, Any]:
        """Load the configuration from a .env file"""
        return dotenv.dotenv_values(stream=io.StringIO(conf))


class EnvJ2Loader(EnvLoader, J2ModifierMixin):
    """Env file loader with Jinja2 support"""


class EnvLiqLoader(EnvLoader, LiqModifierMixin):
    """Env file loader with Liquid support"""
