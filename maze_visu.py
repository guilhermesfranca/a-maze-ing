from typing import Any, Tuple
from parse_config import MazeConfig, export_maze
from maze_gen import MazeGen
from mlx import Mlx
import random
import os


class MazeVisualizer:
    """Renders the maze using MLX lib"""
    def __init__(self, config: MazeConfig) -> None:
        """Initiatilize instance variables"""
        self.config: MazeConfig = config
        self.generator: MazeGen = MazeGen(config.width, config.height)
        self.cells = self.generator.generate(self.config.perfect)
        self.resolution: list[Tuple[int, int]] = []
        self.options: dict[str, str]

        # Default colors
        self.wall_color = bytes([0x6E, 0x57, 0x3C, 0xFF])
        self.ft_color = bytes([0xFF, 0x00, 0x00, 0xFF])
        self.path_color = bytes([0x00, 0xD7, 0xFF, 0xFF])
        self.entry_color = bytes([0x50, 0xC8, 0x78, 0xFF])
        self.exit_color = bytes([0x50, 0x53, 0xEF, 0xFF])

        # MLX state variables
        self.mlx: Any
        self.mlx_ptr: Any
        self.win_ptr: Any
        self.img_ptr: Any
        self.data: Any
        self.sl: Any
        self.size = 20

    # Default Menu Options
    def print_menu(self) -> None:
        options = {
            "[SPACE]": "Generate a new Maze",
            "[R]": "Show / Hide Resolution",
            "[C]": "Change Maze Color"
        }
        menu_options = " | ".join(
            f"{key} {value}" for key, value in options.items())
        size = len(menu_options) * 10
        self.mlx.mlx_string_put(self.mlx_ptr, self.win_ptr,
                                (1920 // 2) - (size // 2), 970,
                                0xffffff, menu_options)

    def random_bright_bgra_color(
            self,
            min: int = 80,
            max: int = 255,
            alpha: int = 0xFF
            ) -> bytes:
        """Returns a random wall color as BGRA bytes"""
        return bytes([
            random.randint(min, max),
            random.randint(min, max),
            random.randint(min, max),
            alpha
            ])

    def draw_rect(
            self, x_start: int, y_start: int,
            w: int, h: int, color: bytes
            ) -> None:
        """Draws inside a maze cell
           Receives w and h to define how many pixels to color (wall).
        """
        for y in range(y_start, y_start + h):
            for x in range(x_start, x_start + w):
                offset = (y * self.sl) + (x * 4)
                self.data[offset:offset + 4] = color

    def draw_maze(self, size: int) -> None:
        """Draws the maze onto the buffer."""
        for grid_x_y, dir in self.cells.items():
            x_start = grid_x_y[0] * size + size
            y_start = grid_x_y[1] * size + size

            # Completely enclosed cell (e.g., part of the "42" logo).
            if all(dir[i] for i in ["N", "S", "E", "W"]):
                self.draw_rect(
                    x_start + 2, y_start + 2,
                    size - 4, size - 4, self.ft_color)

            # Entry
            if self.config.entry == grid_x_y:
                self.draw_rect(
                    x_start + 3, y_start + 3,
                    size - 7, size - 7, self.entry_color)

            # Exit
            if self.config.exit_cell == grid_x_y:
                self.draw_rect(
                    x_start + 3, y_start + 3,
                    size - 7, size - 7, self.exit_color)

            # Walls
            if dir["N"]:
                self.draw_rect(
                    x_start, y_start, size, 2, self.wall_color)

            if dir["S"]:
                self.draw_rect(
                    x_start, y_start + size - 2, size, 2,
                    self.wall_color)

            if dir["E"]:
                self.draw_rect(
                    x_start + size - 2, y_start, 2, size,
                    self.wall_color)

            if dir["W"]:
                self.draw_rect(
                    x_start, y_start, 2, size,
                    self.wall_color)

        total_w = self.config.width * self.size
        total_h = self.config.height * self.size

        # Borda externa Norte (superior)
        self.draw_rect(18, 18, total_w + 4, 2, self.wall_color)
        # Borda externa Sul (inferior)
        self.draw_rect(18, total_h + 20, total_w + 4, 2, self.wall_color)
        # Borda externa Oeste (esquerda)
        self.draw_rect(18, 18, 2, total_h + 4, self.wall_color)
        # Borda externa Leste (direita)
        self.draw_rect(total_w + 20, 18, 2, total_h + 4, self.wall_color)

    def path_draw(self, result: list[Tuple[int, int]]) -> None:
        """Generates the resolution when "R" key is pressed."""
        x, y = result[0]
        x = x * self.size + self.size + self.size // 2
        y = y * self.size + self.size + self.size // 2
        self.draw_rect(x, y, 1, 1, self.path_color)
        for next_x, next_y in result[1:]:
            next_x = next_x * self.size + self.size + self.size // 2
            next_y = next_y * self.size + self.size + self.size // 2
            self.draw_rect(
                min(x, next_x), min(y, next_y),
                abs(next_x - x) + 1, abs(next_y - y) + 1,
                self.path_color)
            x, y = next_x, next_y
        x, y = result[0]
        x = x * self.size + self.size + self.size // 2 - 1
        y = y * self.size + self.size + self.size // 2 - 1
        self.draw_rect(x, y, 1, 1, self.path_color)
        for next_x, next_y in result[1:]:
            next_x = next_x * self.size + self.size + self.size // 2 - 1
            next_y = next_y * self.size + self.size + self.size // 2 - 1
            self.draw_rect(
                min(x, next_x), min(y, next_y),
                abs(next_x - x) + 1, abs(next_y - y) + 1,
                self.path_color)
            x, y = next_x, next_y

    def create_image(self) -> None:
        self.data[:] = bytes([0xf0, 0xf0, 0xf0, 0xFF]) * (len(self.data) // 4)

    def make(self) -> None:
        """Start the window"""
        def on_key(key: Any, param: Any) -> None:
            """Start a key listener on release"""
            # ESC
            if key == 65307:
                os._exit(0)

        def on_keypress(key: Any, param: Any) -> None:
            """Start a key listener on release"""
            if key == 32:
                # Regenerate the maze cells
                self.cells = self.generator.generate(self.config.perfect)
                export_maze(self.cells, self.config)

                # Creates a new image
                self.create_image()

                # Draw into the new buffer.
                self.draw_maze(self.size)
                self.resolution = []

                # Print to the screen
                self.mlx.mlx_put_image_to_window(
                    self.mlx_ptr, self.win_ptr, self.img_ptr,
                    start_width, start_height - 20)

            if key == 99 or key == 67:
                # Change wall colors pressin "C"
                self.wall_color = self.random_bright_bgra_color()

                # Creates a new image
                self.create_image()

                # Draw into the new buffer
                self.draw_maze(self.size)
                if self.resolution:
                    self.path_draw(self.resolution)

                # Display the new image in the window
                self.mlx.mlx_put_image_to_window(
                    self.mlx_ptr, self.win_ptr, self.img_ptr,
                    start_width, start_height - 20)

            if key == 82 or key == 114:  # R ou r
                # Generate the solution for the current maze
                if not self.resolution:
                    self.resolution = self.generator.resolution(
                        self.config.entry, self.config.exit_cell)
                    self.path_draw(self.resolution)

                    # Display the image in the window with the current image
                    self.mlx.mlx_put_image_to_window(
                        self.mlx_ptr, self.win_ptr, self.img_ptr,
                        start_width, start_height - 20)
                else:
                    self.create_image()
                    self.draw_maze(self.size)
                    self.mlx.mlx_put_image_to_window(
                        self.mlx_ptr, self.win_ptr, self.img_ptr,
                        start_width, start_height - 20)
                    self.resolution = []

        # Image Size.
        width: int = self.config.width * self.size
        height: int = self.config.height * self.size

        # The image is displayed on the screen starting at these coordinates
        start_width = (1920 // 2) - (width // 2) - self.size
        start_height = (1000 // 2) - (height // 2) - self.size

        self.mlx = Mlx()
        self.mlx_ptr = self.mlx.mlx_init()
        self.win_ptr = self.mlx.mlx_new_window(
            self.mlx_ptr, 1920, 1000, "a-maze-ing")

        # Enable keyboard input
        self.mlx.mlx_key_hook(self.win_ptr, on_key, None)
        self.mlx.mlx_hook(self.win_ptr, 2, 1, on_keypress, None)
        self.mlx.mlx_do_key_autorepeaton(self.mlx_ptr)

        # X button in the top corner of the window
        self.mlx.mlx_hook(self.win_ptr, 33, 0, lambda p: os._exit(0), None)

        # generate the image the first time
        self.img_ptr = self.mlx.mlx_new_image(
            self.mlx_ptr, width + (self.size * 2), height + (self.size * 2))
        self.data, bpp, self.sl, fmt = self.mlx.mlx_get_data_addr(self.img_ptr)
        self.create_image()

        # desenha o labirinto pela primeira vez
        self.draw_maze(self.size)
        export_maze(self.cells, self.config)

        self.print_menu()
        self.mlx.mlx_put_image_to_window(
            self.mlx_ptr, self.win_ptr, self.img_ptr,
            start_width, start_height - 20)

        self.mlx.mlx_loop(self.mlx_ptr)
