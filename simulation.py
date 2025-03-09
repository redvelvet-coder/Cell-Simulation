import random
import time
from model import Patch, Cell
from visualiser import Visualiser
from config import Configuration

class Simulation:
    """
    Manages the simulation lifecycle:
      - Initializes a toroidal grid of patches.
      - Seeds initial cells.
      - Processes simulation ticks (aging, division, death, overcrowding).
      - Updates the visualiser if enabled.
      - Reports statistics at the end.
    """
    def __init__(self, config: Configuration) -> None:
        self.config = config
        self.config.validate()

        # Ensure minimum grid size
        assert self.config.grid_rows >= 3 and self.config.grid_cols >= 3, "Grid size must be at least 3x3."

        # Create a 2D grid of Patch objects.
        self.grid = [
            [Patch(row, col) for col in range(self.config.grid_cols)]
            for row in range(self.config.grid_rows)
        ]

        # Simulation statistics.
        self.current_tick = 0
        self.total_cells_created = 0
        self.total_deaths = 0
        self.deaths_by_age = 0
        self.deaths_by_division_limit = 0
        self.deaths_by_overcrowding = 0

        # Seed initial cells.
        self._seed_initial_cells()

        # Initialize the visualiser if enabled.
        self.visualiser = None
        if self.config.visualisation_enabled:
            patches_flat = [patch for row in self.grid for patch in row]
            self.visualiser = Visualiser(
                patches=patches_flat,
                rows=self.config.grid_rows,
                cols=self.config.grid_cols,
                grid_lines=True,
                ticks=False,
                window_title="Cell Simulation"
            )

    def _seed_initial_cells(self) -> None:
        """Randomly places the initial cell population on empty patches."""
        positions = [(r, c) for r in range(self.config.grid_rows)
                     for c in range(self.config.grid_cols)]
        random.shuffle(positions)
        for _ in range(self.config.initial_population):
            if not positions:
                break
            r, c = positions.pop()
            patch = self.grid[r][c]
            Cell(patch)
            self.total_cells_created += 1

    def run(self) -> None:
        """Runs the simulation until the time limit is reached or all cells are dead."""
        print("Starting simulation...")
        while self.current_tick < self.config.time_limit:
            if self._all_cells_dead():
                print("All cells have died. Ending simulation early.")
                break

            self._simulate_tick()
            self.current_tick += 1

            if self.visualiser:
                self.visualiser.update()

        print("Simulation finished.")
        self.report()  # <-- Now calls the public report() method

    def _simulate_tick(self) -> None:
        """
        Processes one simulation tick:
          1. Ages each cell.
          2. Schedules cell deaths (by age or division limit).
          3. Attempts cell divisions.
          4. Handles overcrowding.
          5. Applies scheduled cell deaths.
        """
        cells_to_die = {}  # Mapping: Patch -> set of death causes
        births = []        # List of tuples (target_patch, new_cell)

        # 1. Age all cells.
        for row in self.grid:
            for patch in row:
                if patch.has_cell():
                    cell = patch.cell()
                    if cell.is_alive():
                        cell.tick()

        # 2. Schedule deaths due to age or division limit.
        for row in self.grid:
            for patch in row:
                if patch.has_cell():
                    cell = patch.cell()
                    if not cell.is_alive():
                        continue
                    if cell.age() >= self.config.age_limit:
                        cells_to_die.setdefault(patch, set()).add("age")
                    if cell.divisions() >= self.config.division_limit:
                        cells_to_die.setdefault(patch, set()).add("division_limit")

        # 3. Attempt cell divisions.
        for r in range(self.config.grid_rows):
            for c in range(self.config.grid_cols):
                patch = self.grid[r][c]
                if patch.has_cell():
                    cell = patch.cell()
                    if not cell.is_alive():
                        continue
                    if patch in cells_to_die:
                        continue
                    if cell.last_division() < self.config.division_cooldown:
                        continue
                    empty_neighbors = self._empty_neighbors(r, c)
                    if empty_neighbors:
                        if random.random() < self.config.division_probability:
                            target_r, target_c = random.choice(empty_neighbors)
                            target_patch = self.grid[target_r][target_c]
                            new_cell = cell.divide(target_patch)
                            births.append((target_patch, new_cell))
                            self.total_cells_created += 1
                            if cell.divisions() >= self.config.division_limit:
                                cells_to_die.setdefault(patch, set()).add("division_limit")
                    else:
                        # Overcrowding: no empty neighbor.
                        self._handle_overcrowding(r, c, cells_to_die)

        # 4. Apply scheduled cell deaths.
        for patch, causes in cells_to_die.items():
            if patch.has_cell():
                cell = patch.cell()
                if cell.is_alive():
                    cell.die()
                    self.total_deaths += 1
                    if "age" in causes:
                        self.deaths_by_age += 1
                    if "division_limit" in causes:
                        self.deaths_by_division_limit += 1
                    if "overcrowding" in causes:
                        self.deaths_by_overcrowding += 1

    def _empty_neighbors(self, row: int, col: int) -> list:
        """Returns a list of (row, col) coordinates for empty patches adjacent to (row, col)."""
        empty = []
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr = (row + dr) % self.config.grid_rows
                nc = (col + dc) % self.config.grid_cols
                if not self.grid[nr][nc].has_cell():
                    empty.append((nr, nc))
        return empty

    def _handle_overcrowding(self, row: int, col: int, cells_to_die: dict) -> None:
        """Handles death by overcrowding in a 3×3 region."""
        region_coords = []
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                nr = (row + dr) % self.config.grid_rows
                nc = (col + dc) % self.config.grid_cols
                region_coords.append((nr, nc))
        region_cells = []
        for r, c in region_coords:
            patch = self.grid[r][c]
            if patch.has_cell():
                cell = patch.cell()
                if cell.is_alive():
                    region_cells.append((patch, cell.age()))
        if region_cells:
            max_age = max(age for (_, age) in region_cells)
            oldest_patches = [patch for (patch, age) in region_cells if age == max_age]
            target_patch = random.choice(oldest_patches)
            cells_to_die.setdefault(target_patch, set()).add("overcrowding")

    def _all_cells_dead(self) -> bool:
        """Returns True if no living cells remain in the grid."""
        for row in self.grid:
            for patch in row:
                if patch.has_cell() and patch.cell().is_alive():
                    return False
        return True

    def report(self) -> None:
        """Displays the final simulation statistics."""
        print("\n--- Simulation Report ---")
        print(f"Total Ticks Simulated: {self.current_tick}")
        print(f"Total Cells Created: {self.total_cells_created}")
        print(f"Total Deaths: {self.total_deaths}")
        print(f"Deaths by Age Limit: {self.deaths_by_age}")
        print(f"Deaths by Division Limit: {self.deaths_by_division_limit}")
        print(f"Deaths by Overcrowding: {self.deaths_by_overcrowding}")
        print("------------------------\n")