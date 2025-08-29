import json
from typing import Any, Dict

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

        with open(conf) as f:
            return json.load(f)


class JsonsLoader(NoConvertingPathMixin, JsonLoader):
    """Json string loader"""

    def loading(self, conf: Any, ignore_nonexist: bool) -> Dict[str, Any]:
        """Load the configuration from a json file"""
        return json.loads(conf)
