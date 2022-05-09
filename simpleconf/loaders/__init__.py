from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from ..caster import cast

if TYPE_CHECKING:
    from diot import Diot


class Loader(ABC):

    CASTERS = None

    @abstractmethod
    def loading(self, conf: Any) -> "Diot":
        """Load the configuration from the path or configurations"""

    def load(self, conf: Any) -> "Diot":
        """Load the configuration from the path or configurations and cast
        values

        Args:
            conf: The configuration file to load

        Returns:
            The Diot object
        """
        if self.__class__.CASTERS:
            return cast(self.loading(conf), self.__class__.CASTERS)
        return self.loading(conf)


    load_with_profiles = load
