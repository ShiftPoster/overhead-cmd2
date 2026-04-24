from argparse import Namespace
from pathlib import Path

from cmd2 import Cmd, CommandSet, with_argparser, with_default_category
from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    CliPositionalArg,
    CliSubCommand,
)
from rich import print

from overhead_cmd2.adapter import ModelAdapter, SettingsAdapter


class DirList(BaseModel):
    path: CliPositionalArg[Path] = Path.cwd()
    extra: Path = Path.cwd()

    def main(self):
        print(self.model_dump())


class Init(BaseModel):
    directory: CliPositionalArg[str]


class Clone(BaseModel):
    repository: CliPositionalArg[str]
    directory: CliPositionalArg[str]


class Git(BaseSettings):
    clone: CliSubCommand[Clone]
    init: CliSubCommand[Init]

    def main(self):
        print(self.model_dump())


@with_default_category("My Commands")
class DirCommandSet(CommandSet):
    dir_adapter = ModelAdapter(DirList)
    dir_adapter.add_path_completer("path", "extra")

    @with_argparser(dir_adapter.parser)
    def do_dir(self, args: Namespace):
        self.dir_adapter.set_cli_run(DirList.main)
        self.dir_adapter.run(args)


@with_default_category("My Commands")
class GitCommandSet(CommandSet):
    git_adapter = SettingsAdapter(Git)
    git_adapter.add_path_completer("directory", "clone.directory")

    @with_argparser(git_adapter.parser)
    def do_git(self, args: Namespace):
        self.git_adapter.set_cli_run(Git.main)
        self.git_adapter.run(args)


if __name__ == "__main__":
    Cmd(auto_load_commands=True).cmdloop()
