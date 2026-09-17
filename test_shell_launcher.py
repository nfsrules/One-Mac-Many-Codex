"""Exercise shell preparation in temporary folders; never opens the app."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


@unittest.skipUnless(os.uname().sysname == "Darwin", "macOS stat syntax")
class ShellTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.root = self.base / "profile with spaces"

    def prepare(self):
        return subprocess.run(
            ["/bin/bash", "-c", 'source "$1"; umask 077; prepare_profile "$2"',
             "test", str(Path(__file__).with_name("launcher.sh")), str(self.root)],
            capture_output=True, text=True)

    def test_private_profile_and_existing_data_preserved(self):
        result = self.prepare()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.root.stat().st_mode & 0o777, 0o700)
        config = self.root / "codex/config.toml"
        self.assertEqual(config.stat().st_mode & 0o777, 0o600)
        sentinel = self.root / "desktop/sentinel"
        sentinel.write_text("keep")
        self.assertEqual(self.prepare().returncode, 0)
        self.assertEqual(sentinel.read_text(), "keep")

    def test_unknown_directory_refused(self):
        self.root.mkdir()
        self.assertNotEqual(self.prepare().returncode, 0)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_symlink_config_cannot_overwrite_target(self):
        self.assertEqual(self.prepare().returncode, 0)
        target = self.base / "primary"
        target.write_text("primary settings")
        config = self.root / "codex/config.toml"
        config.unlink()
        config.symlink_to(target)
        self.assertNotEqual(self.prepare().returncode, 0)
        self.assertEqual(target.read_text(), "primary settings")

    def test_symlink_root_refused(self):
        target = self.base / "primary"
        target.mkdir()
        self.root.symlink_to(target)
        self.assertNotEqual(self.prepare().returncode, 0)
        self.assertEqual(list(target.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
