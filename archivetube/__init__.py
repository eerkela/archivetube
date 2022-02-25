import inspect
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
VIDEO_DIR = Path(ROOT_DIR, "videos")


def error_trace(*args, stack_index: int = 1):
    """Returns a quick trace to the calling namespace for a function/method,
    in case of an error.  Object instances supplied to *args have their
    class names prepended to the message, separated by '.' characters.
    """
    objects = [obj.__class__.__name__ for obj in args]
    calling_func = inspect.stack()[stack_index].function
    if len(objects) > 0:
        return f"{'.'.join(objects)}.{calling_func}"
    return f"{calling_func}"
