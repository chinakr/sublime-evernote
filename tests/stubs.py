"""Minimal stubs of the Sublime Text API so that ``sublime_evernote``
can be imported (and its pure logic tested) outside of Sublime Text.

Usage::

    import stubs
    stubs.install()
    import sublime_evernote  # noqa: E402
"""

import sys
import types

_STUBS_INSTALLED = False


def install():
    """Insert fake ``sublime`` and ``sublime_plugin`` modules into
    ``sys.modules``. Idempotent."""
    global _STUBS_INSTALLED
    if _STUBS_INSTALLED:
        return

    sublime = types.ModuleType("sublime")

    class Region(object):
        def __init__(self, a, b=None):
            self.a = a
            self.b = a if b is None else b

        def __repr__(self):
            return "Region(%r, %r)" % (self.a, self.b)

    def _noop(*args, **kwargs):
        pass

    sublime.Region = Region
    sublime.version = lambda: "4000"
    sublime.platform = lambda: "osx"
    sublime.arch = lambda: "x64"
    sublime.status_message = _noop
    sublime.error_message = _noop
    sublime.message = _noop
    sublime.ok_cancel_dialog = lambda *a, **kw: True
    sublime.yes_no_dialog = lambda *a, **kw: True
    sublime.set_timeout = _noop
    sublime.set_timeout_async = _noop
    sublime.set_clipboard = _noop
    sublime.get_clipboard = lambda: ""
    sublime.load_settings = lambda *a, **kw: types.SimpleNamespace(
        get=lambda *a, **kw: None, set=_noop, add_on_change=_noop)
    sublime.save_settings = _noop
    sublime.find_resources = lambda *a, **kw: []
    sublime.active_window = _noop
    sublime.windows = lambda: []

    sublime_plugin = types.ModuleType("sublime_plugin")

    class TextCommand(object):
        pass

    class WindowCommand(object):
        pass

    class EventListener(object):
        pass

    sublime_plugin.TextCommand = TextCommand
    sublime_plugin.WindowCommand = WindowCommand
    sublime_plugin.EventListener = EventListener

    sys.modules["sublime"] = sublime
    sys.modules["sublime_plugin"] = sublime_plugin
    _STUBS_INSTALLED = True


def ensure_paths():
    """Make repo root (for the plugin) and this directory (for stubs)
    importable regardless of how the tests are launched."""
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(here)
    for path in (root, here):
        if path not in sys.path:
            sys.path.insert(0, path)
