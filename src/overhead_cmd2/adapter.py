from argparse import ArgumentParser, Namespace
from collections.abc import Callable
from functools import partial

from cmd2 import Cmd2ArgumentParser, Cmd
from pydantic import BaseModel
from pydantic_settings import BaseSettings, CliApp, CliSettingsSource


class BaseAdapter:
    Settings: type[BaseSettings]
    parser: ArgumentParser
    settings_source: CliSettingsSource

    def create_parser(self, *args, **kwargs) -> ArgumentParser:
        return Cmd2ArgumentParser()

    def add_completer(self, dest_mapping: dict[str, Callable]) -> list[str]:
        dests = list(dest_mapping.keys())
        for action in self.parser._actions:
            if not dests:
                break
            if action.dest in dests:
                dests.pop(dests.index(action.dest))
                action.completer = dest_mapping[action.dest]  # type: ignore
        return dests

    def add_path_completer(self, *dest: str) -> list[str]:
        return self.add_completer({_: Cmd.path_complete for _ in set(dest)})

    def set_cli_run(self, method: Callable, *args, **kwargs):
        setattr(self.Settings, "cli_run", partial(method, *args, **kwargs))

    def run(self, args: Namespace):
        return CliApp.run(
            self.Settings, cli_settings_source=self.settings_source, cli_args=args
        )


class SettingsAdapter(BaseAdapter):
    def __init__(
        self,
        settings: type[BaseSettings],
    ) -> None:
        self.Settings = settings
        self.parser = self.create_parser()
        self.settings_source = CliSettingsSource(self.Settings, root_parser=self.parser)


class ModelAdapter(SettingsAdapter):
    Model: type[BaseModel]

    def __init__(
        self,
        model: type[BaseModel],
        settings: type[BaseSettings] = BaseSettings,
    ) -> None:
        self.Model = model
        Settings = type(
            "Settings",
            (settings, model),
            {},
        )
        super().__init__(settings=Settings)
