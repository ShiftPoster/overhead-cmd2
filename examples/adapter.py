from argparse import Namespace
from pathlib import Path

from cmd2 import Cmd, CommandSet, with_default_category, with_argparser
from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    CliPositionalArg,
    CliSubCommand,
)
from rich import print

from overhead_cmd2.cmd import BaseModelAdapter, BaseSettingsAdapter


class DirList(BaseModel):
    path: CliPositionalArg[Path] = Path.cwd()

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
    dir_adapter = BaseModelAdapter(DirList)
    dir_adapter.apply_completer({"path": Cmd.path_complete})

    @with_argparser(dir_adapter.parser)
    def do_dir(self, args: Namespace):
        print(args)
        self.dir_adapter.cli_run(args)


@with_default_category("My Commands")
class GitCommandSet(CommandSet):
    git_adapter = BaseSettingsAdapter(Git)

    @with_argparser(git_adapter.parser)
    def do_git(self, args: Namespace):
        print(args)
        self.git_adapter.cli_run(args)


if __name__ == "__main__":
    Cmd(auto_load_commands=True).cmdloop()
