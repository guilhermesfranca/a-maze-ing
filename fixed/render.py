"""MiniLibX rendering and event handling for the maze application."""

import sys
from pathlib import Path
from typing import Any, Optional, Tuple

from config import Config
from mazegen import Maze, MazeError, MazeGenerator
from mazegen.maze import DIRECTIONS


class MazeWindow:
    """Own the MLX window, its image, and its interaction state."""

    def __init__(
        self, config: Config, generator: MazeGenerator, maze: Maze
    ) -> None:
        """Initialize rendering state without opening a window."""
        self.config = config
        self.generator = generator
        self.maze = maze
        self.cell_size = 20
        self.width = (maze.width + 2) * self.cell_size
        self.height = (maze.height + 2) * self.cell_size
        self.show_path = False
        self.color_index = 0
        self.colors = ((0, 0, 255, 255), (255, 0, 255, 255),
                       (0, 255, 255, 255), (255, 255, 255, 255))
        self.mlx: Any = None
        self.context: Any = None
        self.window: Any = None
        self.image: Any = None
        self.data: Any = None
        self.stride = 0
        self.error: Optional[str] = None

    def _rect(
        self, x: int, y: int, width: int, height: int,
        color: Tuple[int, int, int, int]
    ) -> None:
        """Paint a rectangle with BGRA pixels in the MLX buffer."""
        row = bytes(color) * width
        for line in range(y, y + height):
            offset = line * self.stride + x * 4
            self.data[offset:offset + len(row)] = row

    def _draw(self) -> None:
        """Clear and redraw the complete maze and optional solution."""
        size = self.cell_size
        for y in range(self.height):
            offset = y * self.stride
            self.data[offset:offset + self.width * 4] = (
                bytes((0, 0, 0, 255)) * self.width
            )
        wall = self.colors[self.color_index]
        for y, row in enumerate(self.maze.walls):
            for x, cell in enumerate(row):
                px, py = (x + 1) * size, (y + 1) * size
                if (x, y) in self.maze.blocked:
                    self._rect(px + 2, py + 2, size - 4, size - 4,
                               (255, 0, 0, 255))
                if cell & 1:
                    self._rect(px, py, size, 2, wall)
                if cell & 2:
                    self._rect(px + size - 2, py, 2, size, wall)
                if cell & 4:
                    self._rect(px, py + size - 2, size, 2, wall)
                if cell & 8:
                    self._rect(px, py, 2, size, wall)
        if self.show_path:
            x, y = self.maze.entry
            moves = {name: (dx, dy) for name, dx, dy, _, _ in DIRECTIONS}
            for direction in self.maze.shortest_path():
                dx, dy = moves[direction]
                cx, cy = (x + 1) * size + size // 2, (
                    (y + 1) * size + size // 2
                )
                self._rect(min(cx, cx + dx * size) - 2,
                           min(cy, cy + dy * size) - 2,
                           abs(dx) * size + 4, abs(dy) * size + 4,
                           (0, 180, 255, 255))
                x, y = x + dx, y + dy
        for point, color in ((self.maze.entry, (0, 255, 255, 255)),
                             (self.maze.exit, (0, 255, 0, 255))):
            self._rect((point[0] + 1) * size + 5,
                       (point[1] + 1) * size + 5, size - 10, size - 10,
                       color)
        self.mlx.mlx_put_image_to_window(
            self.context, self.window, self.image, 0, 0
        )

    def _key(self, key: int, param: object) -> None:
        """Handle regeneration, path display, wall colors and quit."""
        try:
            if key == 65307:
                self.mlx.mlx_loop_exit(self.context)
                return
            if key == 32:
                maze = self.generator.generate(
                    self.config.entry, self.config.exit, self.config.perfect
                )
                Path(self.config.output_file).write_text(
                    maze.to_text(), encoding="utf-8"
                )
                self.maze = maze
            elif key in (112, 80):
                self.show_path = not self.show_path
            elif key in (99, 67):
                self.color_index = (self.color_index + 1) % len(self.colors)
            else:
                return
            self._draw()
        except (MazeError, OSError, RuntimeError) as exc:
            self.error = str(exc)
            print(f"Erro: {exc}", file=sys.stderr)
            self.mlx.mlx_loop_exit(self.context)

    def _close(self, param: object) -> None:
        """Stop the event loop when the window is closed."""
        self.mlx.mlx_loop_exit(self.context)

    def run(self) -> None:
        """Create MLX resources, process events, and release resources."""
        try:
            from mlx import Mlx
        except ImportError as exc:
            raise ImportError(
                "Instale a MiniLibX Python para Linux; veja o README."
            ) from exc
        self.mlx = Mlx()
        self.context = self.mlx.mlx_init()
        if not self.context:
            raise RuntimeError("Não foi possível inicializar a MiniLibX.")
        try:
            self.window = self.mlx.mlx_new_window(
                self.context, self.width, self.height, "A-Maze-ing"
            )
            if not self.window:
                raise RuntimeError("Não foi possível criar a janela.")
            self.image = self.mlx.mlx_new_image(
                self.context, self.width, self.height
            )
            if not self.image:
                raise RuntimeError("Não foi possível criar a imagem.")
            self.data, bpp, self.stride, _ = (
                self.mlx.mlx_get_data_addr(self.image)
            )
            if bpp != 32:
                raise RuntimeError(
                    f"Formato de imagem não suportado: {bpp} bpp"
                )
            self.mlx.mlx_key_hook(self.window, self._key, None)
            self.mlx.mlx_hook(self.window, 33, 0, self._close, None)
            self._draw()
            self.mlx.mlx_loop(self.context)
        finally:
            if self.image:
                self.mlx.mlx_destroy_image(self.context, self.image)
            if self.window:
                self.mlx.mlx_destroy_window(self.context, self.window)
            self.mlx.mlx_release(self.context)
        if self.error:
            raise RuntimeError(self.error)
