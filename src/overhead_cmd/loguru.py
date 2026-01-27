from cmd2 import Cmd, Statement
from loguru import logger, Record

FILE_ONLY_KEY: str = "file_only"
file_logger = logger.bind(**{FILE_ONLY_KEY: True})


def file_only_filter(record: Record) -> bool:
    return record["extra"].get(FILE_ONLY_KEY, False)


class LoguruCmd(Cmd):
    def onecmd(self, statement: Statement | str, *, add_to_history: bool = True) -> bool:
        with file_logger.catch(reraise=True):
            return super().onecmd(statement, add_to_history=add_to_history)
