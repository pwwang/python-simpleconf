from typing import Any
from simpleconf.utils import require_package
from diot import Diot

from . import Loader

yaml = require_package("yaml")


class YamlLoader(Loader):
    """Yaml file loader"""

    def loading(self, conf: Any) -> Diot:
        """Load the configuration from a yaml file"""
        with open(conf) as f:
            return Diot(yaml.load(f, Loader=yaml.FullLoader))
