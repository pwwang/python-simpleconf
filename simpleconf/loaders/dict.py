from typing import Any
from diot import Diot

from . import Loader


class DictLoader(Loader):
    """Dict loader"""

    def loading(self, conf: Any) -> Diot:
        """Load the configuration from a dict"""
        return Diot(conf)
