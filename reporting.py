# reporting.py

def generate_report(simulation) -> None:
    """
    Generates a report based on simulation statistics.
    
    The simulation object is expected to have the following attributes:
      - current_tick
      - total_cells_created
      - total_deaths
      - deaths_by_age
      - deaths_by_division_limit
      - deaths_by_overcrowding
    """
    print("\n--- Simulation Report ---")
    print(f"Time covered by simulation (ticks): {simulation.current_tick}")
    print(f"Total number of cells created:       {simulation.total_cells_created}")
    print(f"Total number of deaths:              {simulation.total_deaths}")
    print("Breakdown of causes of death:")
    print(f"  Age limit:         {simulation.deaths_by_age}")
    print(f"  Division limit:    {simulation.deaths_by_division_limit}")
    print(f"  Overcrowding:      {simulation.deaths_by_overcrowding}")
    print("-------------------------")
