from importlib import util

import pytest

LOGURU: str = "loguru"


@pytest.mark.importorskip(
    LOGURU, reason=f"This test requires optional dependency '{LOGURU}' to be installed."
)
def test_import():
    # run command
    # Check log file? capture logs? need stack trace string
    pass


@pytest.mark.skipif(
    (util.find_spec(LOGURU) is not None),
    reason=f"This test requires optional dependency '{LOGURU}' to NOT be installed.",
)
def test_missing():
    with pytest.raises(ImportError):
        from overhead_cmd2._loguru import LoguruCmd  # noqa: 401
