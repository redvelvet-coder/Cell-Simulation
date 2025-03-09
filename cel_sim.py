from config import Configuration
from simulation import Simulation

def main() -> None:
    # 1. Create and configure simulation parameters
    config = Configuration()
    config.interactive_setup()  # user can change parameters
    
    # 2. Build and run the simulation
    sim = Simulation(config)
    sim.run()
    
    # 3. Display final simulation statistics
    sim.report()

if __name__ == "__main__":
    main()