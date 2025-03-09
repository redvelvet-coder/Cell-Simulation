"""
Configuration module for the cell simulation.

Manages the simulation parameters:
  - grid_rows: Number of grid rows (≥ 3)
  - grid_cols: Number of grid columns (≥ 3)
  - initial_population: Initial number of cells (≥ 1, and ≤ total patches)
  - age_limit: Maximum age in ticks (≥ 1)
  - division_limit: Maximum number of successful divisions (≥ 1)
  - division_probability: Chance for a cell to successfully divide (0 ≤ p ≤ 1)
  - division_cooldown: Minimum ticks between divisions (≥ 1)
  - time_limit: Simulation duration in ticks (≥ 1)
  - visualisation_enabled: Whether to display the simulation graphically (True/False)
"""

class Configuration:
    def __init__(self) -> None:
        self.reset_defaults()

    def reset_defaults(self) -> None:
        """Resets all configuration parameters to their default values."""
        self.grid_rows = 15
        self.grid_cols = 25
        self.initial_population = 2
        self.age_limit = 10
        self.division_limit = 2
        self.division_probability = 0.2
        self.division_cooldown = 2
        self.time_limit = 100
        self.visualisation_enabled = True
        print("\nConfiguration has been reset to default values.")

    def display(self) -> None:
        """Displays the current configuration parameters."""
        print("\nCurrent Configuration:")
        print("-" * 40)
        print(f"1. Grid rows                : {self.grid_rows}")
        print(f"2. Grid columns             : {self.grid_cols}")
        print(f"3. Initial population       : {self.initial_population}")
        print(f"4. Age limit (ticks)        : {self.age_limit}")
        print(f"5. Division limit           : {self.division_limit}")
        print(f"6. Division probability     : {self.division_probability}")
        print(f"7. Division cooldown (ticks): {self.division_cooldown}")
        print(f"8. Simulation time limit    : {self.time_limit}")
        print(f"9. Visualisation enabled    : {self.visualisation_enabled}")
        print("-" * 40)

    def validate(self) -> None:
        """
        Validates the configuration parameters.

        Raises:
            ValueError: If any parameter does not meet its constraint.
        """
        if self.grid_rows < 3:
            raise ValueError("Grid rows must be at least 3.")
        if self.grid_cols < 3:
            raise ValueError("Grid columns must be at least 3.")
        if self.initial_population < 1:
            raise ValueError("Initial population must be at least 1.")
        if self.initial_population > self.grid_rows * self.grid_cols:
            raise ValueError("Initial population cannot exceed total number of patches "
                             f"({self.grid_rows * self.grid_cols}).")
        if self.age_limit < 1:
            raise ValueError("Age limit must be at least 1.")
        if self.division_limit < 1:
            raise ValueError("Division limit must be at least 1.")
        if not (0 <= self.division_probability <= 1):
            raise ValueError("Division probability must be between 0 and 1.")
        if self.division_cooldown < 1:
            raise ValueError("Division cooldown must be at least 1.")
        if self.time_limit < 1:
            raise ValueError("Time limit must be at least 1.")

    def interactive_setup(self) -> None:
        """
        Displays the main menu and allows the user to run the simulation,
        display/modify configuration, reset to defaults, or exit.
        """
        while True:
            print("\n" + "=" * 50)
            print("            CELL SIMULATION MENU")
            print("=" * 50)
            print("1. Run simulation with current (or default) values")
            print("2. Display and modify configuration")
            print("3. Reset to default values")
            print("4. Exit")
            print("=" * 50)

            choice = input("Enter your choice [1-4]: ").strip()
            if choice == "1":
                try:
                    self.validate()
                    print("\nConfiguration valid. Proceeding to run simulation...\n")
                    break
                except ValueError as e:
                    print(f"Configuration error: {e}\nPlease modify your settings first.")
            elif choice == "2":
                self._configuration_menu()
            elif choice == "3":
                self.reset_defaults()
            elif choice == "4":
                print("Exiting program. Goodbye!")
                exit(0)
            else:
                print("Invalid option. Please choose a number between 1 and 4.")

    def _configuration_menu(self) -> None:
        """
        Nested menu to display and modify individual configuration parameters.
        """
        while True:
            self.display()
            print("Modify parameters:")
            print("a. Set grid rows")
            print("b. Set grid columns")
            print("c. Set initial population")
            print("d. Set age limit (ticks)")
            print("e. Set division limit")
            print("f. Set division probability")
            print("g. Set division cooldown (ticks)")
            print("h. Set simulation time limit (ticks)")
            print("i. Toggle visualisation enabled")
            print("x. Return to main menu")

            option = input("Enter your option [a-i or x]: ").strip().lower()
            if option == "a":
                self.grid_rows = self._prompt_int("Enter number of grid rows (≥ 3): ", 3)
            elif option == "b":
                self.grid_cols = self._prompt_int("Enter number of grid columns (≥ 3): ", 3)
            elif option == "c":
                val = self._prompt_int("Enter initial cell population (≥ 1): ", 1)
                if val > self.grid_rows * self.grid_cols:
                    print(f"Error: Value cannot exceed total patches ({self.grid_rows * self.grid_cols}).")
                else:
                    self.initial_population = val
            elif option == "d":
                self.age_limit = self._prompt_int("Enter age limit in ticks (≥ 1): ", 1)
            elif option == "e":
                self.division_limit = self._prompt_int("Enter division limit (≥ 1): ", 1)
            elif option == "f":
                self.division_probability = self._prompt_float("Enter division probability (0 to 1): ", 0, 1)
            elif option == "g":
                self.division_cooldown = self._prompt_int("Enter division cooldown (≥ 1): ", 1)
            elif option == "h":
                self.time_limit = self._prompt_int("Enter simulation time limit in ticks (≥ 1): ", 1)
            elif option == "i":
                self.visualisation_enabled = not self.visualisation_enabled
                print(f"Visualisation enabled set to: {self.visualisation_enabled}")
            elif option == "x":
                print("Returning to main menu...")
                break
            else:
                print("Invalid option. Please choose a valid option from the menu.")

    def _prompt_int(self, prompt: str, min_val: int = None) -> int:
        """Prompt for an integer, ensuring it's ≥ min_val if specified."""
        while True:
            try:
                val = int(input(prompt))
                if min_val is not None and val < min_val:
                    print(f"Error: Value must be at least {min_val}.")
                else:
                    return val
            except ValueError:
                print("Error: Please enter a valid integer.")

    def _prompt_float(self, prompt: str, min_val: float = None, max_val: float = None) -> float:
        """Prompt for a float, ensuring it's within [min_val, max_val]."""
        while True:
            try:
                val = float(input(prompt))
                if (min_val is not None and val < min_val) or (max_val is not None and val > max_val):
                    print(f"Error: Value must be between {min_val} and {max_val}.")
                else:
                    return val
            except ValueError:
                print("Error: Please enter a valid number.")