from abc import ABC, abstractmethod
from os import PathLike
from pathlib import Path
from typing import TYPE_CHECKING, Any

from ..caster import cast

if TYPE_CHECKING:
    from diot import Diot


class Loader(ABC):

    CASTERS = None

    @abstractmethod
    def loading(self, conf: Any, ignore_nonexist: bool) -> "Diot":
        """Load the configuration from the path or configurations"""

    def _exists(self, conf: PathLike, ignore_exist: bool) -> bool:
        """Check if the configuration file exists"""
        path = Path(conf)
        if not ignore_exist and not path.exists():
            raise FileNotFoundError(f"{conf} does not exist")
        return path.exists()

    def load(self, conf: Any, ignore_nonexist: bool = False) -> "Diot":
        """Load the configuration from the path or configurations and cast
        values

        Args:
            conf: The configuration file to load

        Returns:
            The Diot object
        """
        loaded = self.loading(conf, ignore_nonexist)
        if self.__class__.CASTERS:
            return cast(loaded, self.__class__.CASTERS)
        return loaded

    load_with_profiles = load
