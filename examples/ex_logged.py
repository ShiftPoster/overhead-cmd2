from argparse import Namespace
from pathlib import Path

from cmd2 import Cmd, Statement
from loguru import logger

file_logger = logger.bind(file_only=True)


class MyCmd(Cmd):
    def onecmd(self, statement: Statement | str, *, add_to_history: bool = True) -> bool:
        with file_logger.catch(reraise=True):
            return super().onecmd(statement, add_to_history=add_to_history)

    def do_error(self, args: Namespace):
        logger.trace(args)
        logger.info("Something doesn't seem right...")
        raise Exception("Whoops!")


if __name__ == "__main__":
    import sys
    logger.remove()
    logger.add(sys.stdout, filter=lambda r: "file_only" not in r["extra"])
    logger.add(Path.cwd() / "logs" / "ex_{time}.log")
    MyCmd().cmdloop()
