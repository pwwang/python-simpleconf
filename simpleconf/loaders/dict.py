from typing import Any, Dict

from . import Loader, NoConvertingPathMixin


class DictLoader(Loader):
    """Dict loader"""

    @staticmethod
    def _convert_path(conf):
        return conf

    def loading(self, conf: Any, ignore_nonexist: bool) -> Dict[str, Any]:
        """Load the configuration from a dict"""
        return conf

    async def a_loading(self, conf: Any, ignore_nonexist: bool) -> Dict[str, Any]:
        """Asynchronously load the configuration from a dict"""
        return conf


class DictsLoader(NoConvertingPathMixin, DictLoader):  # type: ignore[misc]
    """Dict string loader"""

    def loading(self, conf: Any, ignore_nonexist: bool) -> Dict[str, Any]:
        """Load the configuration from a dict"""
        return eval(conf)
