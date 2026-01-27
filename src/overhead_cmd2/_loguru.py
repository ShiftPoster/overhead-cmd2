from __future__ import annotations

from typing import TYPE_CHECKING, Union

from cmd2 import Cmd, Statement

try:
    from loguru import logger

    if TYPE_CHECKING:
        from loguru import Record
except ImportError as err:
    raise ImportError(
        "'loguru' is not installed, run `pip install overhead-cmd2[loguru]`"
    ) from err

FILE_ONLY_KEY: str = "file_only"
_file_logger = logger.bind(**{FILE_ONLY_KEY: True})


def file_only_filter(record: Record) -> bool:
    return not record["extra"].get(FILE_ONLY_KEY, False)


class LoguruCmd(Cmd):
    def onecmd(
        self, statement: Union[Statement, str], *, add_to_history: bool = True
    ) -> bool:
        with _file_logger.catch(reraise=True):
            return super().onecmd(statement, add_to_history=add_to_history)
