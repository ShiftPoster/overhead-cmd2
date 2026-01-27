from argparse import Namespace
from pathlib import Path

from loguru import logger

from overhead_cmd.loguru import LoguruCmd, file_only_filter


class MyCmd(LoguruCmd):
    def do_error(self, args: Namespace):
        logger.trace(args)
        logger.info("Something doesn't seem right...")
        raise Exception("Whoops!")


if __name__ == "__main__":
    import sys
    logger.remove()
    logger.add(sys.stdout, filter=file_only_filter)
    logger.add(Path.cwd() / "logs" / "loguru_{time}.log")
    MyCmd().cmdloop()
