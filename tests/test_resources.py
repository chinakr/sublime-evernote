"""Regression tests for package resource files.

These guard the Package Control submission requirements: menus and
command palette files must stay valid JSON, the settings/key bindings
entries must use ``edit_settings`` with correct ``args``, and every
release listed in ``messages.json`` must exist on disk.
"""

import json
import os
import re
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_resource(name):
    with open(os.path.join(REPO_ROOT, name), encoding="utf-8") as f:
        return json.load(f)


def iter_nodes(data):
    if isinstance(data, dict):
        yield data
        for child in data.get("children") or ():
            for node in iter_nodes(child):
                yield node
    elif isinstance(data, list):
        for entry in data:
            for node in iter_nodes(entry):
                yield node


class TestMainMenu(unittest.TestCase):

    def setUp(self):
        self.menu = load_resource("Main.sublime-menu")

    def find_entries(self, caption):
        return [
            node for node in iter_nodes(self.menu)
            if caption.casefold() in str(node.get("caption", "")).casefold()
        ]

    def test_menu_is_valid_json_list(self):
        self.assertIsInstance(self.menu, list)

    def test_key_bindings_entry_uses_edit_settings(self):
        entries = self.find_entries("key bindings")
        self.assertTrue(entries, "Main.sublime-menu must offer a Key Bindings entry")
        for entry in entries:
            self.assertEqual(entry["command"], "edit_settings")
            base_file = entry["args"]["base_file"]
            self.assertEqual(
                base_file, "${packages}/Evernote/Default.sublime-keymap")
            self.assertEqual(
                entry["args"]["user_file"],
                "${packages}/User/Default (${platform}).sublime-keymap")

    def test_settings_entry_uses_edit_settings(self):
        entries = [
            node for node in iter_nodes(self.menu)
            if node.get("command") == "edit_settings"
            and node.get("args", {}).get("base_file", "").endswith(
                "Evernote.sublime-settings")
        ]
        self.assertTrue(entries, "Main.sublime-menu must offer a Settings entry")
        for entry in entries:
            self.assertIn("default", entry["args"])

    def test_menu_base_files_exist(self):
        for node in iter_nodes(self.menu):
            base_file = node.get("args", {}).get("base_file")
            if base_file:
                # The repository root doubles as the package root, so
                # "${packages}/Evernote/<file>" maps to "<file>" here.
                rel = base_file.replace("${packages}/Evernote/", "")
                self.assertTrue(
                    os.path.isfile(os.path.join(REPO_ROOT, rel)),
                    "menu references missing resource: %s" % base_file)


class TestCommandPalette(unittest.TestCase):

    def test_commands_file_is_valid_json_list(self):
        self.assertIsInstance(load_resource("Default.sublime-commands"), list)

    def test_settings_entry_uses_edit_settings(self):
        commands = load_resource("Default.sublime-commands")
        entries = [
            node for node in commands
            if node.get("command") == "edit_settings"
            and node.get("args", {}).get("base_file", "").endswith(
                "Evernote.sublime-settings")
        ]
        self.assertTrue(
            entries, "Default.sublime-commands must offer an edit_settings "
                     "entry for the package settings")

    def test_settings_entry_caption_convention(self):
        # Package Control review requires palette entries for editing
        # settings to start with "Preferences: <PackageName>".
        commands = load_resource("Default.sublime-commands")
        for node in commands:
            if node.get("command") == "edit_settings":
                caption = str(node.get("caption", ""))
                self.assertTrue(
                    caption.startswith("Preferences: Evernote"),
                    "settings palette entry caption must start with "
                    "'Preferences: Evernote': %s" % caption)
                self.assertIn("Settings", caption)


class TestVersionConsistency(unittest.TestCase):

    def test_messages_declare_current_version(self):
        with open(os.path.join(REPO_ROOT, "messages.json"), encoding="utf-8") as f:
            messages = json.load(f)

        with open(os.path.join(REPO_ROOT, "sublime_evernote.py"),
                  encoding="utf-8") as f:
            match = re.search(r'EVERNOTE_PLUGIN_VERSION\s*=\s*"([^"]+)"', f.read())
        self.assertIsNotNone(match)
        version = match.group(1)

        self.assertIn(version, messages)
        self.assertTrue(os.path.isfile(os.path.join(REPO_ROOT, messages[version])))


if __name__ == "__main__":
    unittest.main()
