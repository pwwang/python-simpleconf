from contextlib import contextmanager
from typing import Any, List

from diot import Diot

from .utils import config_to_ext, get_loader, POOL_KEY, META_KEY


class Config:
    """The configuration class"""

    @staticmethod
    def load(*configs, ignore_nonexist: bool = False) -> Diot:
        """Load the configuration from the files, or other configurations

        Args:
            *configs: The configuration files or other configurations to load
                Latter ones will override the former ones for items with the
                same keys recursively.
            ignore_nonexist: Whether to ignore non-existent files
                Otherwise, will raise errors

        Returns:
            A Diot object with the loaded configurations
        """
        out = Diot()
        for conf in configs:
            ext = config_to_ext(conf)
            loader = get_loader(ext)
            loaded = loader.load(conf, ignore_nonexist)
            out.update(loaded)

        return out

    @staticmethod
    def load_one(
        config, loader: str = None, ignore_nonexist: bool = False
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
            ext = config_to_ext(config)
            loader = get_loader(ext)
        else:
            loader = get_loader(loader)

        return loader.load(config, ignore_nonexist)


class ProfileConfig:
    """The configuration class with profile support"""

    @staticmethod
    def load(*configs: Any, ignore_nonexist: bool = False) -> Diot:
        """Load the configuration from the files, or other configurations

        Args:
            *configs: The configuration files or other configurations to load
                Latter ones will override the former ones for items with the
                same profile and keys recursively.
            ignore_nonexist: Whether to ignore non-existent files
                Otherwise, will raise errors
        """
        out = Diot({POOL_KEY: Diot()})
        pool = out[POOL_KEY]
        out[META_KEY] = {
            "current_profile": None,
            "base_profile": None,
        }
        for conf in configs:
            ext = config_to_ext(conf)
            loader = get_loader(ext)
            loaded = loader.load_with_profiles(conf, ignore_nonexist)
            for profile, value in loaded.items():
                profile = profile.lower()
                pool.setdefault(profile, Diot())
                pool[profile].update(value)

        ProfileConfig.use_profile(out, "default")
        return out

    @staticmethod
    def load_one(
        conf: Any, loader: str = None, ignore_nonexist: bool = False
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
            ext = config_to_ext(conf)
            loader = get_loader(ext)
        else:
            loader = get_loader(loader)

        loaded = loader.load_with_profiles(conf, ignore_nonexist)
        for profile, value in loaded.items():
            profile = profile.lower()
            pool.setdefault(profile, Diot())
            pool[profile].update(value)

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
                out.update(pool[base])
            out[META_KEY]["current_profile"] = profile
            out[META_KEY]["base_profile"] = base
            out.update(pool[profile])
            return out

        # copy = False
        for key in list(conf):
            if key in (POOL_KEY, META_KEY):
                continue
            del conf[key]

        if base is not None:
            conf.update(pool[base])
        conf.update(pool[profile])
        conf[META_KEY]["current_profile"] = profile
        conf[META_KEY]["base_profile"] = base

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
    def with_profile(conf: Diot, profile: str, base: str = "default") -> Diot:
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
