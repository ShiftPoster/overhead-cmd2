import time
from argparse import Namespace

from cmd2 import Cmd, with_category
from rich.console import Console

TEST_CATAGORY: str = "Test Commands"
console = Console()


class MyCmd(Cmd):
    @with_category(TEST_CATAGORY)
    def do_exemplar(self, args: Namespace):
        """This is what the status is expected to look like."""
        with console.status("Working!"):
            for _ in range(10):
                console.log("console.log: Hello from cmd!")
                time.sleep(0.1)

    @with_category(TEST_CATAGORY)
    def do_problem(self, args: Namespace):
        """Demonstrate the problem."""
        with console.status("Working!"):
            for _ in range(10):
                self.pwarning("pwarning: Hello from cmd!")
                time.sleep(0.1)


if __name__ == "__main__":
    MyCmd().cmdloop()
