from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, List, Dict
from pathlib import Path

from diot import Diot
from ..caster import cast


class Loader(ABC):

    CASTERS: List[Callable[[str, bool], Any]] | None = None

    @staticmethod
    def _convert_path(conf: str | Path) -> Path:
        """Convert the conf to Path if it is a string"""
        try:
            from yunpath import AnyPath
        except ImportError:
            AnyPath = Path

        if isinstance(conf, str):
            return AnyPath(conf)
        return conf

    @abstractmethod
    def loading(self, conf: Any, ignore_nonexist: bool) -> Dict[str, Any]:
        """Load the configuration from the path or configurations"""

    def _exists(self, conf: str | Path, ignore_exist: bool) -> bool:
        """Check if the configuration file exists"""
        path = self.__class__._convert_path(conf)
        if not ignore_exist and not path.exists():
            raise FileNotFoundError(f"{conf} does not exist")
        return path.exists()

    def load(self, conf: Any, ignore_nonexist: bool = False) -> Diot:
        """Load the configuration from the path or configurations and cast
        values

        Args:
            conf: The configuration file to load

        Returns:
            The Diot object
        """
        path = self.__class__._convert_path(conf)
        loaded = self.loading(path, ignore_nonexist)
        if self.__class__.CASTERS:
            loaded = cast(loaded, self.__class__.CASTERS)

        return Diot(loaded)

    load_with_profiles = load


class NoConvertingPathMixin(ABC):
    """String loader base class"""

    @staticmethod
    def _convert_path(conf: str) -> str:
        return conf
