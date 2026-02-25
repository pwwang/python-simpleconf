import json
from typing import Any, Awaitable, Dict

from . import (
    Loader,
    NoConvertingPathMixin,
    LoaderModifierMixin,
    J2ModifierMixin,
    LiqModifierMixin,
)


class JsonLoader(Loader, LoaderModifierMixin):
    """Json file loader"""

    def loading(self, conf: Any, ignore_nonexist: bool) -> Dict[str, Any]:
        """Load the configuration from a json file"""
        if hasattr(conf, "read"):
            content = conf.read()
            return json.loads(content)

        if not self._exists(conf, ignore_nonexist):
            return {}

        conf = self.__class__._convert_path(conf)
        content = conf.read_text()
        content = self._modifier(content)
        return json.loads(content)

    async def a_loading(self, conf: Any, ignore_nonexist: bool) -> Dict[str, Any]:
        """Asynchronously load the configuration from a json file"""
        if hasattr(conf, "read"):
            content = conf.read()
            if isinstance(content, Awaitable):
                content = await content
            if isinstance(content, bytes):
                content = content.decode()
            content = self._modifier(content)
            return json.loads(content)

        if not await self._a_exists(conf, ignore_nonexist):
            return {}

        conf = self.__class__._convert_path(conf)
        content = await conf.a_read_text()
        content = self._modifier(content)
        return json.loads(content)


class JsonsLoader(NoConvertingPathMixin, JsonLoader):  # type: ignore[misc]
    """Json string loader"""

    def loading(self, conf: Any, ignore_nonexist: bool) -> Dict[str, Any]:
        """Load the configuration from a json file"""
        return json.loads(conf)


class JsonJ2Loader(JsonLoader, J2ModifierMixin):
    """Json file loader with Jinja2 support"""


class JsonLiqLoader(JsonLoader, LiqModifierMixin):
    """Json file loader with Liquid support"""
