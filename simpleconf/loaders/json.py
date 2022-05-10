import json
from typing import Any

from diot import Diot

from . import Loader


class JsonLoader(Loader):
    """Json file loader"""

    def loading(self, conf: Any, ignore_nonexist: bool) -> Diot:
        """Load the configuration from a json file"""
        if not self._exists(conf, ignore_nonexist):
            return Diot()
        with open(conf) as f:
            return Diot(json.load(f))
