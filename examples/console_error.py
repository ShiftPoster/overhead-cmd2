import time
from argparse import Namespace
from pathlib import Path

from cmd2 import Cmd, with_category
from loguru import logger
from rich.console import Console
from rich.logging import RichHandler

TEST_CATAGORY: str = "Test Commands"
console = Console()


class MyCmd(Cmd):
    @with_category(TEST_CATAGORY)
    def do_exemplar(self, args: Namespace):
        """This is what the status is expected to look like."""
        with console.status("Working!"):
            for _ in range(10):
                logger.info("logger.info: Hello from cmd!")
                time.sleep(0.1)

    @with_category(TEST_CATAGORY)
    def do_problem(self, args: Namespace):
        """Demonstrate the problem."""
        with console.status("Working!"):
            for _ in range(10):
                self.pfeedback("pfeedback: Hello from cmd!")
                time.sleep(0.1)


if __name__ == "__main__":
    logger.remove()
    logger.add(
        RichHandler(console=console), format=lambda _: "{message}", backtrace=False
    )
    logger.add(Path.cwd() / "logs" / "loguru_{time}.log")
    MyCmd().cmdloop()
