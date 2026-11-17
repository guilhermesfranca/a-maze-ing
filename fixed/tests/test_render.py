"""Tests for rendering and key events without a graphical session."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from config import Config
from mazegen import MazeGenerator
from render import MazeWindow


class FakeMLX:
    """Record display and exit calls without loading the native library."""

    def __init__(self) -> None:
        """Initialize call counters."""
        self.frames = 0
        self.exited = False

    def mlx_put_image_to_window(
        self, context: object, window: object, image: object, x: int, y: int
    ) -> None:
        """Record one displayed frame."""
        self.frames += 1

    def mlx_loop_exit(self, context: object) -> None:
        """Record a request to stop the loop."""
        self.exited = True


class RenderTests(unittest.TestCase):
    """Check that event handlers redraw without accumulating old pixels."""

    def test_regeneration_and_controls(self) -> None:
        """Repeated space events replace pixels and synchronize output."""
        with TemporaryDirectory() as directory:
            output = str(Path(directory) / "maze.txt")
            config = Config(10, 8, (0, 0), (9, 7), output, True, 42)
            generator = MazeGenerator(10, 8, 42)
            maze = generator.generate(config.entry, config.exit, True)
            window = MazeWindow(config, generator, maze)
            mlx = FakeMLX()
            window.mlx = mlx
            window.stride = window.width * 4
            window.data = memoryview(bytearray(window.stride * window.height))
            window._draw()
            for _ in range(5):
                window._key(32, None)
                self.assertEqual(Path(output).read_text(encoding="utf-8"),
                                 window.maze.to_text())
                actual = bytes(window.data)
                window.data[:] = b"\xff" * len(window.data)
                window._draw()
                self.assertEqual(bytes(window.data), actual)
            window._key(112, None)
            self.assertTrue(window.show_path)
            window._key(112, None)
            self.assertFalse(window.show_path)
            window._key(99, None)
            self.assertEqual(window.color_index, 1)
            window._key(65307, None)
            self.assertTrue(mlx.exited)
            self.assertIsNone(window.error)


if __name__ == "__main__":
    unittest.main()
