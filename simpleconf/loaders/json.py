import json
from typing import Any

from diot import Diot

from . import Loader


class JsonLoader(Loader):
    """Json file loader"""

    def loading(self, conf: Any) -> Diot:
        """Load the configuration from a json file"""
        with open(conf) as f:
            return Diot(json.load(f))
