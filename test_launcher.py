"""Offline safety checks. Never launches the real app or reads real credentials."""
import os
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import patch

import launcher


class LauncherTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.root = self.base / "profile"

    def test_private_files_and_repeat_launch_preserves_data(self):
        launcher.prepare(self.root)
        config = self.root / "codex" / "config.toml"
        self.assertEqual(stat.S_IMODE(config.stat().st_mode), 0o600)
        for path in (self.root, self.root / "codex", self.root / "desktop"):
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o700)
        credential = self.root / "codex" / "auth.json"
        credential.write_text("fake-test-credential")
        launcher.prepare(self.root)
        self.assertEqual(credential.read_text(), "fake-test-credential")

    def test_unknown_directory_is_untouched(self):
        self.root.mkdir()
        item = self.root / "existing"
        item.write_text("keep")
        with self.assertRaises(RuntimeError):
            launcher.prepare(self.root)
        self.assertEqual(item.read_text(), "keep")
        self.assertEqual(list(self.root.iterdir()), [item])

    def test_symlink_profile_refused(self):
        target = self.base / "primary"
        target.mkdir()
        self.root.symlink_to(target, target_is_directory=True)
        with self.assertRaises(RuntimeError):
            launcher.prepare(self.root)
        self.assertEqual(list(target.iterdir()), [])

    def test_symlink_config_refused_without_altering_target(self):
        launcher.prepare(self.root)
        config = self.root / "codex" / "config.toml"
        config.unlink()
        target = self.base / "primary-config"
        target.write_text("primary settings")
        config.symlink_to(target)
        with self.assertRaises(RuntimeError):
            launcher.prepare(self.root)
        self.assertEqual(target.read_text(), "primary settings")

    def test_changed_auth_config_is_not_overwritten(self):
        launcher.prepare(self.root)
        config = self.root / "codex" / "config.toml"
        config.write_text('cli_auth_credentials_store = "keyring"\n')
        with self.assertRaises(RuntimeError):
            launcher.prepare(self.root)
        self.assertIn('"keyring"', config.read_text())

    @patch("launcher.subprocess.run")
    def test_only_isolated_paths_passed_and_parent_auth_not_inherited(self, run):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "fake", "CODEX_HOME": "/primary",
                                     "CODEX_ACCESS_TOKEN": "fake"}):
            launcher.launch(self.root, self.base, Path("/Applications/ChatGPT.app"))
        args = run.call_args.args[0]
        env = run.call_args.kwargs["env"]
        self.assertIn("CODEX_HOME=" + str(self.root / "codex"), args)
        self.assertIn("CODEX_ELECTRON_USER_DATA_PATH=" + str(self.root / "desktop"), args)
        self.assertNotIn("OPENAI_API_KEY", env)
        self.assertNotIn("CODEX_ACCESS_TOKEN", env)
        self.assertNotIn("CODEX_HOME", env)
        self.assertFalse(run.call_args.kwargs.get("shell", False))

    @patch("launcher.subprocess.run")
    def test_process_detection_ignores_primary_and_helpers(self, run):
        app = Path("/Applications/ChatGPT.app")
        binary = str(app / "Contents/MacOS/ChatGPT")
        flag = "--user-data-dir=" + str(self.root / "desktop")
        run.return_value.stdout = "11 " + binary + "\n22 " + binary + " " + flag + "\n33 helper " + flag
        self.assertEqual(launcher.running_pids(self.root, app, "ChatGPT"), [22])


if __name__ == "__main__":
    unittest.main()
