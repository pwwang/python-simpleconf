from typing import Any
from simpleconf.utils import require_package
from diot import Diot

from . import Loader

yaml = require_package("yaml")


class YamlLoader(Loader):
    """Yaml file loader"""

    def loading(self, conf: Any, ignore_nonexist: bool) -> Diot:
        """Load the configuration from a yaml file"""
        if hasattr(conf, "read"):
            content = conf.read()
            return Diot(yaml.load(content, Loader=yaml.FullLoader))

        if not self._exists(conf, ignore_nonexist):
            return Diot()

        with open(conf) as f:
            return Diot(yaml.load(f, Loader=yaml.FullLoader))
