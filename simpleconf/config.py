from __future__ import annotations

from contextlib import contextmanager
from typing import Any, List, Generator, TypeAlias, Union, Sequence

from diot import Diot

from .utils import config_to_ext, get_loader, POOL_KEY, META_KEY
from .loaders import Loader

LoaderType: TypeAlias = Union[str, Loader, None]


class Config:
    """The configuration class"""

    @staticmethod
    def load(
        *configs: Any,
        loader: LoaderType | Sequence[LoaderType] = None,
        ignore_nonexist: bool = False,
    ) -> Diot:
        """Load the configuration from the files, or other configurations

        Args:
            *configs: The configuration files or other configurations to load
                Latter ones will override the former ones for items with the
                same keys recursively.
            loader: The loader to use. If a list is given, it must have the
                same length as configs.
            ignore_nonexist: Whether to ignore non-existent files
                Otherwise, will raise errors

        Returns:
            A Diot object with the loaded configurations
        """
        if not isinstance(loader, Sequence) or isinstance(loader, str):
            loader = [loader] * len(configs)

        if len(loader) != len(configs):
            raise ValueError(
                f"Length of loader ({len(loader)}) does not match "
                f"length of configs ({len(configs)})"
            )

        out = Diot()
        for i, conf in enumerate(configs):
            loaded = Config.load_one(conf, loader[i], ignore_nonexist)
            out.update_recursively(loaded)

        return out

    @staticmethod
    def load_one(
        config,
        loader: str | Loader | None = None,
        ignore_nonexist: bool = False,
    ) -> Diot:
        """Load the configuration from the file

        Args:
            config: The configuration file to load
            loader: The loader to use
            ignore_nonexist: Whether to ignore non-existent files
                Otherwise, will raise errors

        Returns:
            A Diot object with the loaded configuration
        """
        if loader is None:
            if hasattr(config, "read"):
                raise ValueError("'loader' must be specified for stream")

            ext = config_to_ext(config)
            loader = get_loader(ext)
        else:
            loader = get_loader(loader)

        return loader.load(config, ignore_nonexist)


class ProfileConfig:
    """The configuration class with profile support"""

    @staticmethod
    def load(
        *configs: Any,
        loader: LoaderType | Sequence[LoaderType] = None,
        ignore_nonexist: bool = False,
    ) -> Diot:
        """Load the configuration from the files, or other configurations

        Args:
            *configs: The configuration files or other configurations to load
                Latter ones will override the former ones for items with the
                same profile and keys recursively.
            loader: The loader to use. If a list is given, it must have the
                same length as configs.
            ignore_nonexist: Whether to ignore non-existent files
                Otherwise, will raise errors
        """
        if not isinstance(loader, Sequence) or isinstance(loader, str):
            loader = [loader] * len(configs)

        if len(loader) != len(configs):
            raise ValueError(
                f"Length of loader ({len(loader)}) does not match "
                f"length of configs ({len(configs)})"
            )

        out = Diot({POOL_KEY: Diot()})
        pool = out[POOL_KEY]
        out[META_KEY] = {
            "current_profile": None,
            "base_profile": None,
        }
        for i, conf in enumerate(configs):
            lder = loader[i]

            if lder is None and hasattr(conf, "read"):
                raise ValueError("'loader' must be specified for stream")

            if lder is None:
                ext = config_to_ext(conf)
                lder = get_loader(ext)
            else:
                lder = get_loader(lder)

            loaded = lder.load_with_profiles(conf, ignore_nonexist)
            for profile, value in loaded.items():
                profile = profile.lower()
                pool.setdefault(profile, Diot())
                pool[profile].update_recursively(value)

        ProfileConfig.use_profile(out, "default")
        return out

    @staticmethod
    def load_one(
        conf: Any,
        loader: str | Loader | None = None,
        ignore_nonexist: bool = False,
    ) -> Diot:
        """Load the configuration from the file

        Args:
            conf: The configuration file to load
            loader: The loader to use. Will detect from conf by default
            ignore_nonexist: Whether to ignore non-existent files
                Otherwise, will raise errors

        Returns:
            A Diot object with the loaded configuration
        """

        out = Diot({POOL_KEY: Diot()})
        pool = out[POOL_KEY]
        out[META_KEY] = {
            "current_profile": None,
            "base_profile": None,
        }

        if loader is None:
            if hasattr(conf, "read"):
                raise ValueError("'loader' must be specified for stream")

            ext = config_to_ext(conf)
            loader = get_loader(ext)
        else:
            loader = get_loader(loader)

        loaded = loader.load_with_profiles(conf, ignore_nonexist)
        for profile, value in loaded.items():
            profile = profile.lower()
            pool.setdefault(profile, Diot())
            pool[profile].update_recursively(value)

        ProfileConfig.use_profile(out, "default")
        return out

    @staticmethod
    def use_profile(
        conf: Diot,
        profile: str,
        base: str = "default",
        copy: bool = False,
    ) -> Diot:
        """Switch the configuration to the given profile, based on the
        default profile.

        Args:
            conf: The configuration object by the `load` function
            profile: The profile to use
            default: The default profile

        Returns:
            The configuration object with the switched profile if copy is True
            Otherwise None (updated in-place)
        """
        pool = conf[POOL_KEY]
        if copy:
            out = Diot({POOL_KEY: pool, META_KEY: conf[META_KEY].copy()})
            if base is not None:
                out.update_recursively(pool[base])
            out[META_KEY]["current_profile"] = profile
            out[META_KEY]["base_profile"] = base
            out.update_recursively(pool[profile])
            return out

        # copy = False
        for key in list(conf):
            if key in (POOL_KEY, META_KEY):
                continue
            del conf[key]

        if base is not None:
            conf.update_recursively(pool[base])
        conf.update_recursively(pool[profile])
        conf[META_KEY]["current_profile"] = profile
        conf[META_KEY]["base_profile"] = base

        return conf

    @staticmethod
    def current_profile(conf: Diot) -> str:
        """Get the current profile"""
        return conf[META_KEY]["current_profile"]

    @staticmethod
    def base_profile(conf: Diot) -> str:
        """Get the base profile"""
        return conf[META_KEY]["base_profile"]

    @staticmethod
    def detach(conf: Diot) -> Diot:
        """Detach the configurations of current profile from the
        configuration object.
        Profile information will be removed.

        Args:
            conf: The configuration object by the `load` function

        Returns:
            The configurations with the current profile
        """
        out = Diot()
        for key in conf:
            if key in (POOL_KEY, META_KEY):
                continue
            out[key] = conf[key]
        return out

    @staticmethod
    def pool(conf: Diot) -> Diot:
        """Get the pool"""
        return conf[POOL_KEY]

    @staticmethod
    def profiles(conf: Diot) -> List:
        """Get the profiles in the configuration

        Args:
            conf: The configuration object by the `load` function

        Returns:
            The list of profiles
        """
        return list(conf[POOL_KEY])

    @staticmethod
    def has_profile(conf: Diot, profile: str) -> bool:
        """Check if the configuration has the given profile

        Args:
            conf: The configuration object by the `load` function
            profile: The profile to check

        Returns:
            Whether the configuration has the given profile
        """
        return profile in conf[POOL_KEY]

    @staticmethod
    @contextmanager
    def with_profile(
        conf: Diot,
        profile: str,
        base: str = "default",
    ) -> Generator[Diot, None, None]:
        """A context manager to use the given profile

        Args:
            conf: The configuration object by the `load` function
            profile: The profile to use
            base: The base profile

        Yields:
            The configuration object with the switched profile
        """
        prev_profile = ProfileConfig.current_profile(conf)
        prev_base = ProfileConfig.base_profile(conf)
        ProfileConfig.use_profile(conf, profile, base)
        yield conf
        ProfileConfig.use_profile(conf, prev_profile, prev_base)
