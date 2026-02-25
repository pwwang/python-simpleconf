from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, List, Dict
from pathlib import Path

from diot import Diot
from panpath import PanPath
from ..caster import cast


class Loader(ABC):

    CASTERS: List[Callable[[str, bool], Any]] | None = None

    @staticmethod
    def _convert_path(conf: str | Path) -> Path:
        """Convert the conf to Path if it is a string"""
        if isinstance(conf, (str, Path)):
            return PanPath(conf)
        return conf

    @abstractmethod
    def loading(self, conf: Any, ignore_nonexist: bool) -> Dict[str, Any]:
        """Load the configuration from the path or configurations"""

    @abstractmethod
    async def a_loading(self, conf: Any, ignore_nonexist: bool) -> Dict[str, Any]:
        """Asynchronously load the configuration from the path or configurations"""

    @classmethod
    def _convert(cls, conf: Any, loaded: Any) -> Diot:
        """Convert the loaded configuration to Diot"""
        if cls.CASTERS:
            loaded = cast(loaded, cls.CASTERS)

        return Diot(loaded)

    @classmethod
    def _convert_with_profiles(cls, conf: Any, loaded: Any) -> Diot:
        """Convert the loaded configuration with profiles to Diot"""
        return Diot(loaded)

    def _exists(self, conf: str | Path, ignore_exist: bool) -> bool:
        """Check if the configuration file exists"""
        path = self.__class__._convert_path(conf)
        exists = path.exists()
        if not ignore_exist and not exists:
            raise FileNotFoundError(f"{conf} does not exist")
        return exists

    async def _a_exists(self, conf: str | Path, ignore_exist: bool) -> bool:
        """Asynchronously check if the configuration file exists"""
        path = self.__class__._convert_path(conf)
        exists = await path.a_exists()  # type: ignore[attr-defined]
        if not ignore_exist and not exists:
            raise FileNotFoundError(f"{conf} does not exist")
        return exists

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
        return self.__class__._convert(conf, loaded)

    async def a_load(self, conf: Any, ignore_nonexist: bool = False) -> Diot:
        """Asynchronously load the configuration from the path or configurations
        and cast values

        Args:
            conf: The configuration file to load

        Returns:
            The Diot object
        """
        path = self.__class__._convert_path(conf)
        loaded = await self.a_loading(path, ignore_nonexist)
        return self.__class__._convert(conf, loaded)

    def load_with_profiles(  # type: ignore[override]
        self,
        conf: Any,
        ignore_nonexist: bool = False,
    ) -> Diot:
        """Load the configuration from the path or configurations with profiles
        and cast values

        Args:
            conf: The configuration file to load

        Returns:
            The Diot object
        """
        path = self.__class__._convert_path(conf)
        loaded = self.loading(path, ignore_nonexist)
        return self.__class__._convert_with_profiles(conf, loaded)

    async def a_load_with_profiles(  # type: ignore[override]
        self,
        conf: Any,
        ignore_nonexist: bool = False,
    ) -> Diot:
        """Asynchronously load the configuration from the path or configurations
        with profiles and cast values

        Args:
            conf: The configuration file to load

        Returns:
            The Diot object
        """
        path = self.__class__._convert_path(conf)
        loaded = await self.a_loading(path, ignore_nonexist)
        return self.__class__._convert_with_profiles(conf, loaded)


class NoConvertingPathMixin(ABC):
    """String loader base class"""

    @staticmethod
    def _convert_path(conf: str) -> str:
        return conf

    async def a_loading(self, conf: Any, ignore_nonexist: bool) -> Dict[str, Any]:
        """Asynchronously load the configuration from a toml file"""
        return self.loading(conf, ignore_nonexist)  # type: ignore[attr-defined]


class LoaderModifierMixin(ABC):
    """Loader mixin class with content modifier"""

    def _modifier(self, content: str | bytes) -> str | bytes:
        """Modify the content of the configuration file before loading"""
        return content


class J2ModifierMixin(LoaderModifierMixin):
    """Loader mixin class with Jinja2 content modifier"""

    def _modifier(self, content: str | bytes) -> str | bytes:
        """Modify the content of the configuration file before loading"""
        from jinja2 import Template
        return Template(content).render()


class LiqModifierMixin(LoaderModifierMixin):
    """Loader mixin class with Liquid content modifier"""

    def _modifier(self, content: str | bytes) -> str | bytes:
        """Modify the content of the configuration file before loading"""
        from liquid import Liquid
        return Liquid(content, from_file=False, mode="wild").render()
