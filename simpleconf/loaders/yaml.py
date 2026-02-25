from typing import Any, Dict, Awaitable

from . import (
    Loader,
    NoConvertingPathMixin,
    LoaderModifierMixin,
    J2ModifierMixin,
    LiqModifierMixin,
)
from ..utils import require_package

yaml = require_package("yaml")


class YamlLoader(Loader, LoaderModifierMixin):
    """Yaml file loader"""

    def loading(self, conf: Any, ignore_nonexist: bool) -> Dict[str, Any]:
        """Load the configuration from a yaml file"""
        if hasattr(conf, "read"):
            content = conf.read()
            content = self._modifier(content)
            return yaml.load(content, Loader=yaml.FullLoader)

        if not self._exists(conf, ignore_nonexist):
            return {}

        conf = self.__class__._convert_path(conf)
        content = conf.read_text()
        content = self._modifier(content)
        return yaml.load(content, Loader=yaml.FullLoader)

    async def a_loading(self, conf: Any, ignore_nonexist: bool) -> Dict[str, Any]:
        """Asynchronously load the configuration from a yaml file"""
        if hasattr(conf, "read"):
            content = conf.read()
            if isinstance(content, Awaitable):
                content = await content
            if isinstance(content, bytes):
                content = content.decode()
            content = self._modifier(content)
            return yaml.load(content, Loader=yaml.FullLoader)

        if not await self._a_exists(conf, ignore_nonexist):
            return {}

        conf = self.__class__._convert_path(conf)
        content = await conf.a_read_text()
        content = self._modifier(content)
        return yaml.load(content, Loader=yaml.FullLoader)


class YamlsLoader(NoConvertingPathMixin, YamlLoader):  # type: ignore[misc]
    """Yaml string loader"""

    def loading(self, conf: Any, ignore_nonexist: bool) -> Dict[str, Any]:
        """Load the configuration from a yaml file"""
        return yaml.load(conf, Loader=yaml.FullLoader)


class YamlJ2Loader(YamlLoader, J2ModifierMixin):
    """Yaml file loader with Jinja2 support"""


class YamlLiqLoader(YamlLoader, LiqModifierMixin):
    """Yaml file loader with Liquid support"""
