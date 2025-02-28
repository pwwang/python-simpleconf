from typing import Any, Dict

from . import Loader


class DictLoader(Loader):
    """Dict loader"""

    def loading(self, conf: Any, ignore_nonexist: bool) -> Dict[str, Any]:
        """Load the configuration from a dict"""
        return conf


class DictsLoader(DictLoader):
    """Dict string loader"""

    def loading(self, conf: Any, ignore_nonexist: bool) -> Dict[str, Any]:
        """Load the configuration from a dict"""
        return eval(conf)
