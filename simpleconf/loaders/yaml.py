from typing import Any, Dict, Awaitable

from . import Loader, NoConvertingPathMixin
from ..utils import require_package

yaml = require_package("yaml")


class YamlLoader(Loader):
    """Yaml file loader"""

    def loading(self, conf: Any, ignore_nonexist: bool) -> Dict[str, Any]:
        """Load the configuration from a yaml file"""
        if hasattr(conf, "read"):
            content = conf.read()
            return yaml.load(content, Loader=yaml.FullLoader)

        if not self._exists(conf, ignore_nonexist):
            return {}

        conf = self.__class__._convert_path(conf)
        with conf.open("r") as f:
            return yaml.load(f, Loader=yaml.FullLoader)

    async def a_loading(self, conf: Any, ignore_nonexist: bool) -> Dict[str, Any]:
        """Asynchronously load the configuration from a yaml file"""
        if hasattr(conf, "read"):
            content = conf.read()
            if isinstance(content, Awaitable):
                content = await content
            if isinstance(content, bytes):
                content = content.decode()
            return yaml.load(content, Loader=yaml.FullLoader)

        if not await self._a_exists(conf, ignore_nonexist):
            return {}

        async with self.__class__._convert_path(conf).a_open() as f:
            content = await f.read()
            if isinstance(content, bytes):  # pragma: no cover
                content = content.decode()
            return yaml.load(content, Loader=yaml.FullLoader)


class YamlsLoader(NoConvertingPathMixin, YamlLoader):
    """Yaml string loader"""

    def loading(self, conf: Any, ignore_nonexist: bool) -> Dict[str, Any]:
        """Load the configuration from a yaml file"""
        return yaml.load(conf, Loader=yaml.FullLoader)
