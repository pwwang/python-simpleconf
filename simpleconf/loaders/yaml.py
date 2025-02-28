from typing import Any, Dict

from . import Loader
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

        with open(conf) as f:
            return yaml.load(f, Loader=yaml.FullLoader)


class YamlsLoader(YamlLoader):
    """Yaml string loader"""

    def loading(self, conf: Any, ignore_nonexist: bool) -> Dict[str, Any]:
        """Load the configuration from a yaml file"""
        return yaml.load(conf, Loader=yaml.FullLoader)
