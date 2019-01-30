import sys
from threading import Thread

# Workaround for thread exceptions bug

old_run = Thread.run


def run(*args, **kwargs):
    try:
        old_run(*args, **kwargs)
    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception:
        sys.excepthook(*sys.exc_info())


Thread.run = run
