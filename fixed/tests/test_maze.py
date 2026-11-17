"""Behavioral tests for generation, pathfinding and serialization."""

from collections import deque
import unittest

from mazegen import Maze, MazeError, MazeGenerator
from mazegen.maze import DIRECTIONS


class MazeTests(unittest.TestCase):
    """Check graph invariants independently of the graphical interface."""

    def assert_valid(self, maze: Maze, perfect: bool) -> None:
        """Check walls, connectedness, path, cycles and open areas."""
        visited = {maze.entry}
        queue = deque([maze.entry])
        distance = {maze.entry: 0}
        while queue:
            point = queue.popleft()
            for _, neighbor in maze.neighbors(point):
                if neighbor not in visited:
                    visited.add(neighbor)
                    distance[neighbor] = distance[point] + 1
                    queue.append(neighbor)
        expected = {(x, y) for y in range(maze.height)
                    for x in range(maze.width)} - maze.blocked
        self.assertEqual(visited, expected)
        for y in range(maze.height):
            for x in range(maze.width):
                for _, dx, dy, bit, opposite in DIRECTIONS:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < maze.width and 0 <= ny < maze.height:
                        self.assertEqual(bool(maze.walls[y][x] & bit),
                                         bool(maze.walls[ny][nx] & opposite))
                    else:
                        self.assertTrue(maze.walls[y][x] & bit)
        self.assertTrue(all(maze.walls[y][x] == 15 for x, y in maze.blocked))
        position = maze.entry
        for letter in maze.shortest_path():
            available = dict(maze.neighbors(position))
            self.assertIn(letter, available)
            position = available[letter]
        self.assertEqual(position, maze.exit)
        self.assertEqual(len(maze.shortest_path()), distance[maze.exit])
        edges = sum(len(maze.neighbors(p)) for p in visited) // 2
        cycles = edges - len(visited) + 1
        if perfect:
            self.assertEqual(cycles, 0)
        else:
            self.assertGreaterEqual(cycles, 2)
            self.assertLessEqual(
                sum(len(maze.neighbors(p)) == 1 for p in visited), 2
            )
            for y in range(maze.height - 2):
                for x in range(maze.width - 2):
                    self.assertFalse(
                        MazeGenerator._has_open_square(maze, x, y)
                    )
            for p in ((0, 0), (maze.width - 1, 0),
                      (0, maze.height - 1), (maze.width - 1, maze.height - 1),
                      (maze.width // 2, maze.height // 2)):
                self.assertIn(p, visited)
                self.assertTrue(maze.neighbors(p))

    def test_graph_properties(self) -> None:
        """Exercise different dimensions and seeds in both modes."""
        for width, height in ((4, 4), (9, 7), (10, 8), (20, 15), (30, 30)):
            for perfect in (True, False):
                for seed in range(8):
                    with self.subTest(width=width, height=height,
                                      perfect=perfect, seed=seed):
                        maze = MazeGenerator(width, height, seed).generate(
                            (0, 0), (width - 1, height - 1), perfect
                        )
                        self.assert_valid(maze, perfect)

    def test_reproducibility_and_serialization(self) -> None:
        """Verify seed replay and required output shape."""
        first = MazeGenerator(10, 8, 3).generate((0, 0), (9, 7), True)
        second = MazeGenerator(10, 8, 3).generate((0, 0), (9, 7), True)
        self.assertEqual(first.to_text(), second.to_text())
        lines = first.to_text().splitlines()
        self.assertEqual(len(lines), 12)
        self.assertTrue(all(len(line) == 10 for line in lines[:8]))
        self.assertEqual(lines[8:11], ["", "0,0", "9,7"])
        self.assertEqual(lines[11], first.shortest_path())

    def test_invalid_parameters(self) -> None:
        """Reject impossible configurations instead of crashing."""
        with self.assertRaises(MazeError):
            MazeGenerator(1, 2)
        with self.assertRaises(MazeError):
            MazeGenerator(4, 4).generate((0, 0), (0, 0), True)
        with self.assertRaises(MazeError):
            MazeGenerator(4, 4).generate((0, 0), (4, 0), True)
        with self.assertRaises(MazeError):
            MazeGenerator(2, 2, 0).generate((0, 0), (1, 1), False)


if __name__ == "__main__":
    unittest.main()
