import random
from collections import deque
from typing import List, Tuple, Dict


class MazeGen:
    """Create a reproducible DFS Maze with a 42 logo"""
    def __init__(self, width: int, height: int) -> None:
        self.width: int = width
        self.height: int = height
        self.cells: Dict[Tuple[int, int], Dict[str, bool]] = {}

    def generate(
            self, perfect: bool
            ) -> Dict[Tuple[int, int], Dict[str, bool]]:
        """Generate the maze and return the wall structure"""
        self.cells = {
            (x, y): {"N": True, "S": True, "E": True, "W": True}
            for y in range(self.height) for x in range(self.width)
        }
        visited = [
            [False for _ in range(self.width)] for _ in range(self.height)
        ]

        def set_42() -> list[tuple[int, int]]:
            """Mark the cells as Visited to draw the 42 logo"""
            mid_pointx: int = self.width // 2
            midpoint_y: int = self.height // 2
            logo_cells = []
            if self.width % 2:
                start_x, t_x = mid_pointx - 3, mid_pointx + 1
            else:
                start_x, t_x = mid_pointx - 4, mid_pointx + 1
            if self.height % 2:
                start_y, t_y = midpoint_y - 2, midpoint_y - 2
            else:
                start_y, t_y = midpoint_y - 3, midpoint_y - 2
            for i in range(5):
                if i <= 2:
                    logo_cells.append((start_x + 0, start_y + i))
                if i == 2:
                    logo_cells.append((start_x + 1, start_y + i))
                logo_cells.append((start_x + 2, start_y + i))
            for i in range(5):
                if i != 1:
                    logo_cells.append((t_x + 0, t_y + i))
                if i not in [1, 3]:
                    logo_cells.append((t_x + 1, t_y + i))
                if i != 3:
                    logo_cells.append((t_x + 2, t_y + i))
            return logo_cells

        def get_neighbors(x: int, y: int) -> List[Tuple[int, int, str, str]]:
            """Get a list with the possible directions"""
            neighbors = []
            directions = [
                (0, -1, "N", "S"), (0, 1, "S", "N"),
                (-1, 0, "W", "E"), (1, 0, "E", "W")]

            for dx, dy, dir_go, dir_back in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if not visited[ny][nx]:
                        neighbors.append((nx, ny, dir_go, dir_back))

            return neighbors

        start_x, start_y = 0, 0
        visited[start_y][start_x] = True
        stack = [(start_x, start_y)]

        if self.width >= 9 and self.height >= 7:
            logo_cells = set_42()
            for bx, by in logo_cells:
                visited[by][bx] = True

        while stack:
            cx, cy = stack[-1]
            neighbors = get_neighbors(cx, cy)

            if neighbors:
                nx, ny, dir_go, dir_back = random.choice(neighbors)
                self.cells[(cx, cy)][dir_go] = False
                self.cells[(nx, ny)][dir_back] = False
                visited[ny][nx] = True
                stack.append((nx, ny))
            else:
                stack.pop()

        for x in range(self.width):
            self.cells[(x, 0)]["N"] = True
            self.cells[(x, self.height - 1)]["S"] = True
        for y in range(self.height):
            self.cells[(0, y)]["W"] = True
            self.cells[(self.width - 1, y)]["E"] = True

        if not perfect:
            self._do_loops_pacman()

        return self.cells

    def _do_loops_pacman(self) -> None:
        """Break randomly walls when PERFECT = False """
        attempts = (self.width * self.height) // 1
        for _ in range(attempts):
            rx = random.randint(0, self.width - 2)
            ry = random.randint(0, self.height - 2)
            direction = random.choice(["E", "S"])
            cell = self.cells[rx, ry]

            # Check if all walls are closed (42)
            logo_cells = all(cell[d] for d in ["N", "S", "E", "W"])
            if logo_cells:
                continue

            # Try direction E
            if direction == "E" and rx + 1 < self.width:
                cell_e = self.cells[rx + 1, ry]
                logo_cells_e = all(cell_e[d] for d in ["N", "S", "E", "W"])
                if not logo_cells_e:
                    self.cells[(rx, ry)]["E"] = False
                    self.cells[(rx + 1, ry)]["W"] = False
                    continue

            # Try direction S
            if direction == "S" and ry + 1 < self.height:
                cell_s = self.cells[rx, ry + 1]
                logo_cells_s = all(cell_s[d] for d in ["N", "S", "E", "W"])
                if not logo_cells_s:
                    self.cells[(rx, ry)]["S"] = False
                    self.cells[(rx, ry + 1)]["N"] = False

    def resolution(
            self,
            entry: Tuple[int, int],
            exit: Tuple[int, int]
            ) -> list[Tuple[int, int]]:
        """solves the maze with a BFS algorithm"""
        map = self.cells
        if entry not in map or exit not in map:
            raise ValueError("Entry or exit is outside the maze")
        VETORIAL_DIRECTIONS = {
            "N": (0, -1),
            "S": (0, 1),
            "E": (1, 0),
            "W": (-1, 0)}
        queue = deque([(entry, [entry])])
        visited = {entry}
        while queue:
            actual_pos, actual_path = queue.popleft()
            if actual_pos == exit:
                return actual_path
            x, y = actual_pos
            available_path = map[actual_pos]
            for direction, pode_passar in available_path.items():
                if not pode_passar:
                    dx, dy = VETORIAL_DIRECTIONS[direction]
                    neighbor = (x + dx, y + dy)
                    if neighbor in map and neighbor not in visited:
                        visited.add(neighbor)
                        queue.append((neighbor, actual_path + [neighbor]))
        raise ValueError("No path exists between entry and exit")
