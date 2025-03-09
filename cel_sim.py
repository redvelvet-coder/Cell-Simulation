from config import Configuration
from simulation import Simulation

def main() -> None:
    config = Configuration()
    config.interactive_setup()
    sim = Simulation(config)
    sim.run()
    sim.report()

if __name__ == "__main__":
    main()