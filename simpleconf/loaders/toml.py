from typing import Any, Dict, Awaitable

from ..utils import require_package
from ..caster import (
    none_caster,
    null_caster,
)
from . import (
    Loader,
    NoConvertingPathMixin,
    LoaderModifierMixin,
    J2ModifierMixin,
    LiqModifierMixin,
)

toml = require_package("rtoml", "tomllib", "tomli")


class TomlLoader(Loader, LoaderModifierMixin):
    """Toml file loader"""

    CASTERS = [
        none_caster,
        null_caster,
    ]

    def loading(self, conf: Any, ignore_nonexist: bool) -> Dict[str, Any]:
        """Load the configuration from a toml file"""
        if hasattr(conf, "read"):
            content = conf.read()
            content = self._modifier(content)
            return toml.loads(content)

        if not self._exists(conf, ignore_nonexist):
            return {}

        conf = self.__class__._convert_path(conf)
        content = conf.read_bytes()
        try:
            return toml.loads(self._modifier(content))
        except Exception:  # TypeError, TomlParsingError
            content = content.decode()
            content = self._modifier(content)
            return toml.loads(content)

    async def a_loading(self, conf: Any, ignore_nonexist: bool) -> Dict[str, Any]:
        """Asynchronously load the configuration from a toml file"""
        if hasattr(conf, "read"):
            content = conf.read()
            if isinstance(content, Awaitable):
                content = await content
            if isinstance(content, bytes):
                content = content.decode()
            content = self._modifier(content)
            return toml.loads(content)

        if not await self._a_exists(conf, ignore_nonexist):
            return {}

        conf = self.__class__._convert_path(conf)
        content = await conf.a_read_bytes()
        try:
            return toml.loads(self._modifier(content))
        except Exception:  # TypeError, TemplateSyntaxError
            content = content.decode()
            content = self._modifier(content)
            return toml.loads(content)


class TomlsLoader(NoConvertingPathMixin, TomlLoader):  # type: ignore[misc]
    """Toml string loader"""

    def loading(self, conf: Any, ignore_nonexist: bool) -> Dict[str, Any]:
        """Load the configuration from a toml file"""
        return toml.loads(conf)


class TomlJ2Loader(TomlLoader, J2ModifierMixin):
    """Toml file loader with Jinja2 support"""


class TomlLiqLoader(TomlLoader, LiqModifierMixin):
    """Toml file loader with Liquid support"""
