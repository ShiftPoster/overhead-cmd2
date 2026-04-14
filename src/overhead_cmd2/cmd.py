from argparse import ArgumentParser, Namespace
from typing import Dict, Optional, Type, Union

from cmd2 import Cmd, Cmd2ArgumentParser, Cmd2AttributeWrapper, with_argparser
from pydantic import BaseModel
from pydantic_settings import BaseSettings, CliSettingsSource, CliApp


class BaseSettingsAdapter:
    Settings: type[BaseSettings]
    parser: ArgumentParser
    settings_source: CliSettingsSource

    def create_parser(self, *args, **kwargs) -> ArgumentParser:
        return Cmd2ArgumentParser()

    def __init__(
        self,
        settings: type[BaseSettings],
    ) -> None:
        self.Settings = settings
        self.parser = self.create_parser()
        self.settings_source = CliSettingsSource(self.Settings, root_parser=self.parser)

    def cli_run(self, args: Namespace):
        return CliApp.run(self.Settings, cli_settings_source=self.settings_source, cli_args=args)


class BaseModelAdapter(BaseSettingsAdapter):
    Model: type[BaseModel]
    Settings: type[BaseSettings]
    parser: ArgumentParser
    settings_source: CliSettingsSource

    def __init__(
        self,
        model: type[BaseModel],
        cli_run_attr: str = "main",
        settings: type[BaseSettings] = BaseSettings,
    ) -> None:
        self.Model = model
        Settings = type(
            "Settings",
            (settings, model),
            {"cli_run": getattr(model, cli_run_attr)},
        )
        super().__init__(settings=Settings)


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
