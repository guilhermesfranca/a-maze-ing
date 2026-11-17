"""Tests for configuration validation."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from config import load_config
from mazegen import MazeError


class ConfigTests(unittest.TestCase):
    """Validate successful input and useful errors."""

    def test_valid_and_invalid_configs(self) -> None:
        """Require complete, well-formed options and boolean values."""
        valid = ("WIDTH=10\nHEIGHT=8\nENTRY=0,0\nEXIT=9,7\n"
                 "OUTPUT_FILE=maze.txt\nPERFECT=True\nSEED=7\n")
        with TemporaryDirectory() as directory:
            path = Path(directory) / "config.txt"
            path.write_text(valid, encoding="utf-8")
            self.assertEqual(load_config(str(path)).seed, 7)
            for invalid in (
                valid.replace("PERFECT=True", "PERFECT=maybe"),
                valid.replace("WIDTH=10\n", ""),
                valid + "WIDTH=8\n",
                valid + "broken line\n",
                valid.replace("ENTRY=0,0", "ENTRY=0,0,1"),
            ):
                path.write_text(invalid, encoding="utf-8")
                with self.assertRaises(MazeError):
                    load_config(str(path))


if __name__ == "__main__":
    unittest.main()
