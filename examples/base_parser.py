from argparse import Namespace
from datetime import datetime
from pathlib import Path
from shutil import disk_usage

from cmd2 import Cmd, CommandSet, with_default_category
from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    CliPositionalArg,
    CliSubCommand,
)
from rich import print
from rich.table import Table

from overhead_cmd import strip_cmd2_wrapped, with_model_parser


class DirList(BaseModel):
    path: CliPositionalArg[Path] = Path.cwd()

    def main(self):
        self.path = self.path.absolute()
        try:
            paths = tuple(self.path.iterdir())
            directory = self.path
        except NotADirectoryError:
            paths = (self.path,)
            directory = self.path.parent

        table = Table(
            title=f"Directory of {directory}", caption_justify="left", title_style=""
        )
        table.add_column("Date", highlight=True)
        table.add_column("Time", highlight=True)
        table.add_column("Size", highlight=True, justify="right")
        table.add_column("Name", highlight=True)

        file_sizes = []
        num_dirs = 0
        for path in paths:
            stat = path.stat()
            if path.is_file():
                file_sizes.append(stat.st_size)
            else:
                num_dirs += 1
            date = datetime.fromtimestamp(stat.st_mtime)
            table.add_row(
                date.strftime("%m/%d/%Y"),
                date.strftime("%I:%M %p"),
                f"{stat.st_size:,}" if path.is_file() else "",
                path.name,
            )

        table.caption = f"{len(file_sizes)} File(s) {sum(file_sizes)}"
        table.caption += (
            f"\n{num_dirs} Dir(s) {disk_usage(self.path).free:,} bytes free"
        )

        print()
        print(table)
        print()


@with_default_category("Directory Commands")
class DirCommandSet(CommandSet):
    @with_model_parser(DirList)
    def do_list(self, args: Namespace):
        DirList(**strip_cmd2_wrapped(args)).main()


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


@with_default_category("Git Commands")
class GitCommandSet(CommandSet):
    @with_model_parser(Git)
    def do_git(self, args: Namespace):
        # FIXME
        """
        (Cmd) git init
        usage: git init [-h] DIRECTORY
        AttributeError: 'RawDescriptionHelpFormatter' object has no attribute 'console'

        To enable full traceback, run the following command: set debug true
        """
        Git(**strip_cmd2_wrapped(args)).main()


class MyCmd(Cmd):
    def __init__(self):
        super().__init__(auto_load_commands=True)


if __name__ == "__main__":
    MyCmd().cmdloop()
