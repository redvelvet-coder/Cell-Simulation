"""
Simulation module for the cell simulation.

This module defines the Simulation class which:
  - Builds a toroidal grid of Patch objects directly from model.py.
  - Initializes the grid and places cells based on configuration.
  - Runs the simulation tick-by-tick, handling cell aging, division,
    and death (with multiple causes recorded).
  - Updates the visualiser (if enabled) and reports final statistics.

The simulation requirements:
  - The grid is toroidal.
  - Cells divide if conditions are met (empty neighbor available, within division limits,
    division cooldown has passed, and division probability check passes).
  - A cell dies when it reaches its age limit, division limit, or due to overcrowding.
  - A single cell may have multiple causes of death.
"""

import random
from model import Cell, Patch
from visualiser import Visualiser  # provided module; do not modify

class Simulation:
    def __init__(self, config) -> None:
        self.config = config
        self.time_limit: int = config.time_limit
        self.current_tick: int = 0
        self.cells: list = []        # All cells ever created.
        self.alive_cells: list = []  # Currently alive cells.

        # Build a grid (2D list) of Patch objects using Patch from model.py.
        self.patches = [
            [Patch(row, col) for col in range(config.grid_cols)]
            for row in range(config.grid_rows)
        ]

        # Statistics
        self.total_cells_created: int = 0
        self.total_deaths: int = 0
        self.death_causes: dict = {"age": 0, "division": 0, "overcrowding": 0}

        self.initialize_cells()

        if config.visualisation_enabled:
            patches_flat = [patch for row in self.patches for patch in row]
            self.visualiser = Visualiser(
                patches_flat,
                config.grid_rows,
                config.grid_cols,
                grid_lines=True,
                ticks=False,
                window_title="Cell Simulation"
            )
        else:
            self.visualiser = None

    def initialize_cells(self) -> None:
        """Randomly place the initial cells on free patches."""
        available_patches = [patch for row in self.patches for patch in row]
        random.shuffle(available_patches)
        count = 0
        for patch in available_patches:
            if count >= self.config.initial_population:
                break
            if not patch.has_cell():
                cell = Cell(patch)
                self.cells.append(cell)
                self.alive_cells.append(cell)
                self.total_cells_created += 1
                count += 1

    def run(self) -> None:
        """
        Run the simulation until the time limit is reached or all cells are dead.
        Updates the visualiser (if enabled) each tick.
        """
        while self.current_tick < self.config.time_limit and self.alive_cells:
            self.current_tick += 1
            self.simulation_tick()
            if self.visualiser:
                self.visualiser.update()
        print("Simulation ended.")
        if self.visualiser:
            self.visualiser.wait_close()

    def simulation_tick(self) -> None:
        """
        Process one tick: update cell ages, attempt division, and check death conditions.
        """
        # Step 1: Age all alive cells.
        for cell in list(self.alive_cells):
            if cell.is_alive():
                cell.tick()

        # Step 2: Attempt division for eligible cells.
        for cell in list(self.alive_cells):
            if not cell.is_alive():
                continue
            if (cell.divisions() < self.config.division_limit and
                    cell.last_division() >= self.config.division_cooldown):
                neighbors = self.get_neighbors(cell.patch())
                empty_neighbors = [patch for patch in neighbors if not patch.has_cell()]
                if empty_neighbors and random.random() <= self.config.division_probability:
                    chosen_patch = random.choice(empty_neighbors)
                    new_cell = cell.divide(chosen_patch)
                    self.cells.append(new_cell)
                    self.alive_cells.append(new_cell)
                    self.total_cells_created += 1

        # Step 3: Check death conditions (natural and overcrowding).
        for cell in list(self.alive_cells):
            if not cell.is_alive():
                continue

            causes = set()
            if cell.age() >= self.config.age_limit:
                causes.add("age")
            if cell.divisions() >= self.config.division_limit:
                causes.add("division")
            neighbors = self.get_neighbors(cell.patch())
            if all(neighbor.has_cell() for neighbor in neighbors):
                causes.add("overcrowding")

            if causes:
                if cell in self.alive_cells:
                    self.alive_cells.remove(cell)
                if cell.is_alive():
                    cell.die()
                    self.total_deaths += 1
                for cause in causes:
                    self.death_causes[cause] += 1

    def get_neighbors(self, patch: Patch) -> list:
        """
        Return the eight neighboring patches of the given patch,
        using toroidal wrap-around.
        """
        neighbors = []
        row = patch.row()
        col = patch.col()
        for d_row in [-1, 0, 1]:
            for d_col in [-1, 0, 1]:
                if d_row == 0 and d_col == 0:
                    continue
                new_row = (row + d_row) % self.config.grid_rows
                new_col = (col + d_col) % self.config.grid_cols
                neighbors.append(self.patches[new_row][new_col])
        return neighbors

    def get_region(self, patch: Patch, radius: int = 1) -> list:
        """
        Return the square region of patches centered on the given patch,
        with the specified radius.
        """
        region = []
        row = patch.row()
        col = patch.col()
        for d_row in range(-radius, radius + 1):
            for d_col in range(-radius, radius + 1):
                new_row = (row + d_row) % self.config.grid_rows
                new_col = (col + d_col) % self.config.grid_cols
                region.append(self.patches[new_row][new_col])
        return region

    def report(self) -> None:
        """Display simulation statistics."""
        print("\nSimulation Report")
        print("-----------------")
        print(f"Time covered by simulation: {self.current_tick} ticks")
        print(f"Total cells created: {self.total_cells_created}")
        print(f"Total deaths: {self.total_deaths}")
        print("Breakdown of causes of death:")
        print(f"  Age limit:         {self.deaths_by_age}")
        print(f"  Division limit:    {self.deaths_by_division_limit}")
        print(f"  Overcrowding:      {self.deaths_by_overcrowding}")

    @property
    def deaths_by_age(self) -> int:
        return self.death_causes.get("age", 0)

    @property
    def deaths_by_division_limit(self) -> int:
        return self.death_causes.get("division", 0)

    @property
    def deaths_by_overcrowding(self) -> int:
        return self.death_causes.get("overcrowding", 0)