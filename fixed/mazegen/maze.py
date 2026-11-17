"""Generate mazes using randomized depth-first search."""

from collections import deque
from dataclasses import dataclass
import random
from typing import Dict, List, Optional, Set, Tuple

Point = Tuple[int, int]
DIRECTIONS = (
    ("N", 0, -1, 1, 4),
    ("E", 1, 0, 2, 8),
    ("S", 0, 1, 4, 1),
    ("W", -1, 0, 8, 2),
)
PATTERN = (
    "#.#.###",
    "..#...#",
    "###.###",
    "..#.#..",
    "..#.###",
)


class MazeError(ValueError):
    """Report invalid maze parameters or an impossible generation."""


@dataclass
class Maze:
    """A maze with row-major wall masks, reserved cells and endpoints."""

    width: int
    height: int
    entry: Point
    exit: Point
    walls: List[List[int]]
    blocked: Set[Point]

    def neighbors(self, point: Point) -> List[Tuple[str, Point]]:
        """Return reachable neighboring cells and their direction letters."""
        x, y = point
        result = []
        for name, dx, dy, bit, _ in DIRECTIONS:
            nx, ny = x + dx, y + dy
            if (0 <= nx < self.width and 0 <= ny < self.height
                    and not self.walls[y][x] & bit):
                result.append((name, (nx, ny)))
        return result

    def shortest_path(self) -> str:
        """Return a shortest path from entry to exit as NESW letters."""
        previous: Dict[Point, Optional[Tuple[Point, str]]] = {
            self.entry: None
        }
        queue = deque([self.entry])
        while queue and self.exit not in previous:
            point = queue.popleft()
            for direction, neighbor in self.neighbors(point):
                if neighbor not in previous:
                    previous[neighbor] = (point, direction)
                    queue.append(neighbor)
        if self.exit not in previous:
            raise MazeError("A saída não é acessível a partir da entrada.")
        path: List[str] = []
        current = self.exit
        while current != self.entry:
            step = previous[current]
            if step is None:
                raise MazeError("Caminho inconsistente.")
            current, direction = step
            path.append(direction)
        return "".join(reversed(path))

    def to_text(self) -> str:
        """Serialize the wall masks, endpoints and shortest path."""
        rows = ["".join(format(cell, "X") for cell in row)
                for row in self.walls]
        rows.extend(("", f"{self.entry[0]},{self.entry[1]}",
                     f"{self.exit[0]},{self.exit[1]}",
                     self.shortest_path()))
        return "\n".join(rows) + "\n"


class MazeGenerator:
    """Create reproducible DFS mazes with an optional 42 pattern.

    Args:
        width: Number of columns.
        height: Number of rows.
        seed: Optional random seed.
    """

    def __init__(
        self, width: int, height: int, seed: Optional[int] = None
    ) -> None:
        """Store dimensions and initialize an independent random generator."""
        if width < 2 or height < 2:
            raise MazeError("WIDTH e HEIGHT devem ser pelo menos 2.")
        self.width = width
        self.height = height
        self.rng = random.Random(seed)

    def generate(self, entry: Point, exit: Point, perfect: bool) -> Maze:
        """Generate a maze and return its wall structure and path API."""
        for point in (entry, exit):
            if not (0 <= point[0] < self.width
                    and 0 <= point[1] < self.height):
                raise MazeError("Entrada e saída devem estar dentro da grade.")
        if entry == exit:
            raise MazeError("Entrada e saída devem ser diferentes.")
        blocked: Set[Point] = set()
        if self.width >= 9 and self.height >= 7:
            left = self.width // 2 - 3
            top = self.height // 2 - 2
            blocked = {(left + x, top + y)
                       for y, row in enumerate(PATTERN)
                       for x, pixel in enumerate(row) if pixel == "#"}
        if entry in blocked or exit in blocked:
            raise MazeError("Entrada ou saída está dentro do padrão 42.")
        for _ in range(50 if not perfect else 1):
            maze = self._generate_once(entry, exit, blocked)
            if perfect or self._braid(maze):
                return maze
        raise MazeError(
            "Não foi possível gerar um tabuleiro jogável para este tamanho."
        )

    def _generate_once(
        self, entry: Point, exit: Point, blocked: Set[Point]
    ) -> Maze:
        """Create a spanning tree using iterative randomized DFS."""
        maze = Maze(self.width, self.height, entry, exit,
                    [[15] * self.width for _ in range(self.height)], blocked)
        visited = {entry}
        stack = [entry]
        while stack:
            x, y = stack[-1]
            candidates = []
            for _, dx, dy, bit, opposite in DIRECTIONS:
                point = (x + dx, y + dy)
                if (0 <= point[0] < self.width
                        and 0 <= point[1] < self.height
                        and point not in blocked and point not in visited):
                    candidates.append((point, bit, opposite))
            if not candidates:
                stack.pop()
                continue
            point, bit, opposite = self.rng.choice(candidates)
            self._open(maze, (x, y), point, bit, opposite)
            visited.add(point)
            stack.append(point)
        if len(visited) != self.width * self.height - len(blocked):
            raise MazeError("O padrão 42 impede a conectividade desta grade.")
        return maze

    @staticmethod
    def _open(
        maze: Maze, start: Point, end: Point, bit: int, opposite: int
    ) -> None:
        """Remove a shared wall on both sides."""
        maze.walls[start[1]][start[0]] &= ~bit
        maze.walls[end[1]][end[0]] &= ~opposite

    @staticmethod
    def _has_open_square(maze: Maze, x: int, y: int) -> bool:
        """Check whether a 3x3 region has all internal walls open."""
        return (
            all(not maze.walls[y + dy][x + dx] & 2
                for dy in range(3) for dx in range(2))
            and all(not maze.walls[y + dy][x + dx] & 4
                    for dy in range(2) for dx in range(3))
        )

    def _braid(self, maze: Maze) -> bool:
        """Remove walls to reduce dead ends without open 3x3 areas."""
        center = (self.width // 2, self.height // 2)
        if center in maze.blocked:
            raise MazeError("O centro está bloqueado pelo padrão 42.")
        points = [(x, y) for y in range(self.height)
                  for x in range(self.width) if (x, y) not in maze.blocked]
        self.rng.shuffle(points)
        for point in points:
            if len(maze.neighbors(point)) != 1:
                continue
            candidates = []
            x, y = point
            for _, dx, dy, bit, opposite in DIRECTIONS:
                neighbor = (x + dx, y + dy)
                if (0 <= neighbor[0] < self.width
                        and 0 <= neighbor[1] < self.height
                        and neighbor not in maze.blocked
                        and maze.walls[y][x] & bit):
                    candidates.append((neighbor, bit, opposite))
            self.rng.shuffle(candidates)
            for neighbor, bit, opposite in candidates:
                self._open(maze, point, neighbor, bit, opposite)
                has_square = any(
                    self._has_open_square(maze, sx, sy)
                    for sy in range(max(0, y - 2),
                                    min(self.height - 3, y) + 1)
                    for sx in range(max(0, x - 2),
                                    min(self.width - 3, x) + 1)
                )
                if not has_square:
                    break
                maze.walls[y][x] |= bit
                maze.walls[neighbor[1]][neighbor[0]] |= opposite
        edges = sum(len(maze.neighbors(point)) for point in points) // 2
        cycles = edges - len(points) + 1
        dead_ends = sum(len(maze.neighbors(point)) == 1 for point in points)
        return cycles >= 2 and dead_ends <= 2
