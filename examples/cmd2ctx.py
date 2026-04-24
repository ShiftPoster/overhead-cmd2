import sys
from contextlib import contextmanager
from typing import IO, Any, Iterator

from cmd2 import Cmd
from cmd2.rich_utils import APP_THEME, RichPrintKwargs, prepare_objects_for_rendering
from cmd2.styles import Cmd2Style
from rich.console import Console, ThemeContext
from rich.highlighter import ReprHighlighter
from rich.style import StyleType
from rich.text import Text
from rich.traceback import Traceback

_DISALLOWED_ATTRIBUTES = {
    "force_terminal": "Passing 'force_terminal' is not allowed. Its behavior is controlled by the 'ALLOW_STYLE' setting.",
    "force_interactive": "Passing 'force_interactive' is not allowed. Its behavior is controlled by the 'ALLOW_STYLE' setting.",
    "theme": "Passing 'theme' is not allowed. Its behavior is controlled by the global APP_THEME and set_theme().",
}


def _on_broken_pipe(self: Console) -> None:
    """Override which raises BrokenPipeError instead of SystemExit."""
    # NOTE: The obvious downside to not subclassing Console
    self.quiet = True
    raise


@contextmanager
def cmd2_state_base(console: Console, **attrs) -> Iterator[ThemeContext]:
    backup = {}
    attrs.setdefault("on_broken_pipe", _on_broken_pipe)

    # These aren't allowed 🙅‍♂️
    # FIXME: these go to private attributes from __init__
    for attr, error in _DISALLOWED_ATTRIBUTES.items():
        if attr in attrs:
            # Naughty! 😒
            raise TypeError(error)

    # Make sure they didnt update something under my 👃
    missing = tuple(_ for _ in attrs if not hasattr(console, _))
    if missing:
        raise AttributeError(f"Console object missing these attributes: {missing}")

    for key, value in attrs.items():
        # Create backup ➡️💾
        backup[key] = getattr(console, key)
        # Make adjustments 🔨
        setattr(console, key, value)

    # Print away 🖨️
    try:
        # NOTE: ⚠️ Never used Console.use_theme, so I'm not sure how well it works ⚠️
        with console.use_theme(APP_THEME) as theme_ctx:
            # NOTE: ❓ not really sure what would be best to yield here ❓
            yield theme_ctx
    finally:
        # Restore backup 💾➡️
        for key, value in backup.items():
            setattr(console, key, value)


@contextmanager
def cmd2_state_general(
    console: Console, file: IO[str] = sys.stdout
) -> Iterator[ThemeContext]:
    with cmd2_state_base(
        console,
        soft_wrap=True,
        _markup=False,
        _emoji=False,
        _highlight=False,
        file=file,
    ) as _:
        yield _


@contextmanager
def cmd2_state_exception(
    console: Console, file: IO[str] = sys.stderr
) -> Iterator[ThemeContext]:
    with cmd2_state_general(console, file=file) as _:
        yield _


@contextmanager
def cmd2_state_argparser(console: Console, file: IO[str]) -> Iterator[ThemeContext]:
    """I am not sure if this one is feasible because i couldnt find references to `Cmd2RichArgparseConsole` in cmd2."""
    with cmd2_state_base(
        console,
        _markup=False,
        _emoji=False,
        _highlight=False,
        file=file,
    ) as _:
        yield _


class MyCmd(Cmd):
    console: Console

    def __init__(self, *args, console: Console | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.console = console if console else Console(file=self.stdout)

    def print_to(
        self,
        file: IO[str],
        *objects: Any,
        sep: str = " ",
        end: str = "\n",
        style: StyleType | None = None,
        soft_wrap: bool = True,
        emoji: bool = False,
        markup: bool = False,
        highlight: bool = False,
        rich_print_kwargs: RichPrintKwargs | None = None,
        **kwargs: Any,  # noqa: ARG002
    ) -> None:
        prepared_objects = prepare_objects_for_rendering(*objects)

        try:
            with cmd2_state_general(self.console, file):
                self.console.print(
                    *prepared_objects,
                    sep=sep,
                    end=end,
                    style=style,
                    soft_wrap=soft_wrap,
                    emoji=emoji,
                    markup=markup,
                    highlight=highlight,
                    **(rich_print_kwargs if rich_print_kwargs is not None else {}),
                )
        except BrokenPipeError:
            if self.broken_pipe_warning and file != sys.stderr:
                with cmd2_state_general(self.console, file):
                    self.console.print(self.broken_pipe_warning)

    def pexcept(
        self,
        exception: BaseException,
        **kwargs: Any,  # noqa: ARG002
    ) -> None:

        # Only print a traceback if we're in debug mode and one exists.
        if self.debug and sys.exc_info() != (None, None, None):
            traceback = Traceback(
                width=None,  # Use all available width
                code_width=None,  # Use all available width
                show_locals=True,
                max_frames=0,  # 0 means full traceback.
                word_wrap=True,  # Wrap long lines of code instead of truncate
            )
            with cmd2_state_exception(self.console):
                self.console.print(traceback)
                self.console.print()
            return

        # Print the exception in the same style Rich uses after a traceback.
        exception_str = str(exception)

        if exception_str:
            highlighter = ReprHighlighter()

            final_msg = Text.assemble(
                (f"{type(exception).__name__}: ", "traceback.exc_type"),
                highlighter(exception_str),
            )
        else:
            final_msg = Text(f"{type(exception).__name__}", style="traceback.exc_type")

        # If not in debug mode and the 'debug' setting is available,
        # inform the user how to enable full tracebacks.
        if not self.debug and "debug" in self.settables:
            help_msg = Text.assemble(
                "\n\n",
                (
                    "To enable full traceback, run the following command: ",
                    Cmd2Style.WARNING,
                ),
                ("set debug true", Cmd2Style.COMMAND_LINE),
            )
            final_msg.append(help_msg)

        with cmd2_state_exception(self.console):
            self.console.print(final_msg)
            self.console.print()

    def do_print(self, string: str):
        self.poutput(string)
        self.pfeedback(string)
        self.perror(string)
        self.pwarning(string)

    def do_exc(self, *args, **kwargs):
        raise Exception("You have successfully raised an exception!")


if __name__ == "__main__":
    MyCmd().cmdloop()
