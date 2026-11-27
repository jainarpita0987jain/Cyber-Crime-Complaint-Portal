"""Universal escape: typing _esc_ in ANY input cancels the current screen."""
import builtins
import functools
import inspect

ESC = "_esc_"
_real_input = builtins.input


class EscapeInput(Exception):
    pass


def _input(prompt=""):
    value = _real_input(prompt)
    if value.strip().lower() == ESC:
        raise EscapeInput()
    return value


def _guard(fn):
    @functools.wraps(fn)
    def wrapper(*a, **k):
        try:
            return fn(*a, **k)
        except EscapeInput:
            print("\n  (cancelled - _esc_ used)")
    return wrapper


def install(*modules):
    """Patch input() and make every UI function cancel/go back on _esc_."""
    builtins.input = _input
    for m in modules:
        for name, fn in list(vars(m).items()):
            if inspect.isfunction(fn) and fn.__module__ == m.__name__:
                setattr(m, name, _guard(fn))
