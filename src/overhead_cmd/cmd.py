from argparse import ArgumentParser, Namespace
from typing import Dict, Optional, Type, Union

from cmd2 import Cmd, Cmd2ArgumentParser, Cmd2AttributeWrapper, with_argparser
from pydantic import BaseModel
from pydantic_settings import BaseSettings, CliSettingsSource


# TODO: add decorator
def model_to_parser(
    settings: Union[Type[BaseSettings], Type[BaseModel]],
    root_parser: Optional[Union[Cmd2ArgumentParser, ArgumentParser]] = None,
):
    if root_parser is None:
        root_parser = Cmd2ArgumentParser()

    if issubclass(settings, BaseSettings):
        CliSettingsSource(settings, root_parser=root_parser)
    else:
        class Adapter(  # pyright: ignore reportIncompatibleVariableOverride
            BaseSettings, settings
        ):
            pass

        CliSettingsSource(Adapter, root_parser=root_parser)

    return root_parser


def with_model_parser(
    settings: Union[Type[BaseSettings], Type[BaseModel]],
    root_parser: Optional[Union[Cmd2ArgumentParser, ArgumentParser]] = None,
):
    return with_argparser(model_to_parser(settings, root_parser))


def strip_cmd2_wrapped(args: Namespace) -> Dict:
    return {
        k: v for k, v in vars(args).items() if not isinstance(v, Cmd2AttributeWrapper)
    }


class LoggedCmd(Cmd):  # NOTE: mixin instead of subclass?
    pass
