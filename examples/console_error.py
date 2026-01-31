import time
from argparse import Namespace
from pathlib import Path
from threading import Event, Thread
from contextlib import contextmanager
from dataclasses import dataclass, field

from cmd2 import Cmd, with_category
from loguru import logger
from rich.console import Console
from rich.logging import RichHandler

TEST_CATAGORY: str = "Test Commands"
THREAD_CATAGORY: str = "Thread Commands"
console = Console()


@dataclass
class Stuff:
    _stop: Event = field(default_factory=Event)

    @property
    def stopped(self) -> bool:
        return self._stop.is_set()

    def stop(self) -> None:
        return self._stop.set()

    def reset(self) -> None:
        return self._stop.clear()

    def _stuff(self, n: int = 10):
        for _ in range(n):
            if not self.stopped:
                logger.warning("Hello from thread!")
                time.sleep(0.1)
        self.stop()

    @contextmanager
    def launch_thread(self, n: int = 10):
        self.reset()
        thread = Thread(target=logger.catch()(self._stuff), args=(n,))
        try:
            thread.start()
            yield thread
        except KeyboardInterrupt:
            print("^C")
        finally:
            self.stop()
            thread.join()


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
                self.pwarning("pwarning: Hello from cmd!")
                time.sleep(0.1)

    @with_category(THREAD_CATAGORY)
    def do_texemplar(self, args: Namespace):
        stuff = Stuff()
        with stuff.launch_thread():
            with console.status("Working!"):
                while not stuff.stopped:
                    logger.info("logger.info: Hello from cmd!")
                    time.sleep(0.1)

    @with_category(THREAD_CATAGORY)
    def do_tproblem(self, args: Namespace):
        stuff = Stuff()
        with stuff.launch_thread():
            # with console.status("Working!"):
            while not stuff.stopped:
                self.pwarning("pwarning: Hello from cmd!")
                time.sleep(0.1)


if __name__ == "__main__":
    logger.remove()
    logger.add(
        RichHandler(console=console), format=lambda _: "{message}", backtrace=False
    )
    logger.add(Path.cwd() / "logs" / "loguru_{time}.log")
    MyCmd().cmdloop()
