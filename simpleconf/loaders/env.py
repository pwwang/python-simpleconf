from typing import Any
from simpleconf.utils import require_package
from diot import Diot

from ..caster import (
    int_caster,
    float_caster,
    bool_caster,
    none_caster,
    python_caster,
    py_caster,
    json_caster,
    toml_caster,
)
from . import Loader

dotenv = require_package("dotenv")


class EnvLoader(Loader):
    """Env file loader"""

    CASTERS = [
        int_caster,
        float_caster,
        bool_caster,
        none_caster,
        python_caster,
        py_caster,
        json_caster,
        toml_caster,
    ]

    def loading(self, conf: Any) -> Diot:
        """Load the configuration from a .env file"""
        return Diot(dotenv.main.DotEnv(conf).dict())
