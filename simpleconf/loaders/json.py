import json
from typing import Any, Awaitable, Dict

from panpath import PanPath
from . import Loader, NoConvertingPathMixin


class JsonLoader(Loader):
    """Json file loader"""

    def loading(self, conf: Any, ignore_nonexist: bool) -> Dict[str, Any]:
        """Load the configuration from a json file"""
        if hasattr(conf, "read"):
            content = conf.read()
            return json.loads(content)

        if not self._exists(conf, ignore_nonexist):
            return {}

        conf: PanPath = self.__class__._convert_path(conf)
        with conf.open("r") as f:
            return json.load(f)

    async def a_loading(self, conf: Any, ignore_nonexist: bool) -> Dict[str, Any]:
        """Asynchronously load the configuration from a json file"""
        if hasattr(conf, "read"):
            content = conf.read()
            if isinstance(content, Awaitable):
                content = await content
            if isinstance(content, bytes):
                content = content.decode()
            return json.loads(content)

        if not await self._a_exists(conf, ignore_nonexist):
            return {}

        async with self.__class__._convert_path(conf).a_open() as f:
            content = await f.read()
            if isinstance(content, bytes):  # pragma: no cover
                content = content.decode()
            return json.loads(content)


class JsonsLoader(NoConvertingPathMixin, JsonLoader):
    """Json string loader"""

    def loading(self, conf: Any, ignore_nonexist: bool) -> Dict[str, Any]:
        """Load the configuration from a json file"""
        return json.loads(conf)
