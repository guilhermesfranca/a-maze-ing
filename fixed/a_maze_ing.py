"""Run the maze generator and its MiniLibX interface."""

import sys
from pathlib import Path

from config import load_config
from mazegen import MazeError, MazeGenerator
from render import MazeWindow


def main() -> int:
    """Parse the command line and start the application."""
    if len(sys.argv) != 2:
        print("Uso: python3 a_maze_ing.py config.txt", file=sys.stderr)
        return 1
    try:
        config = load_config(sys.argv[1])
        generator = MazeGenerator(config.width, config.height, config.seed)
        maze = generator.generate(config.entry, config.exit, config.perfect)
        if not maze.blocked:
            print("Aviso: o tamanho não permite desenhar o padrão 42.",
                  file=sys.stderr)
        Path(config.output_file).write_text(maze.to_text(), encoding="utf-8")
        print("Controles: espaço = gerar, P = solução, C = cor, Esc = sair")
        MazeWindow(config, generator, maze).run()
    except (MazeError, OSError, ImportError, RuntimeError,
            UnicodeError) as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
