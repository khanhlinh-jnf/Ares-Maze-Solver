# Ares-Maze-Solver
This project implements AI search algorithms to guide Ares through a challenging maze, pushing stones onto switches to unlock a treasure gate. The maze is modeled as a 2D grid where Ares must navigate walls, push weighted stones, and find the optimal path using some search algorithms.

## Project Structure
```
Ares-Maze-Solver/  
│── API/                        # Core logic and algorithm implementation  
│   ├── algorithms.py           # Search algorithms (BFS, A*, etc.)  
│   ├── class_game.py           # Game logic and main game class  
│   ├── func_ui.py              # UI functions for rendering and interactions  
│  
│── assets/                     # Game assets such as sounds and images  
│   ├── resources/              # Stores additional resources  
│   ├── background_music.mp3    # Background music files  
│  
│── input/                      # Input files (e.g., predefined mazes)  
│── output/                     # Output files (e.g., logs, results)  
│── main.py                     # Entry point of the program  
│── README.md                   # Project documentation  
│── report.pdf                  # Detailed project report  
│── requirement.txt              # Dependencies for the project  
│── demo_video.txt               # Contains video link  
```



# Instruction 
Clone the repository to your local workspace:
```bash
git clone https://github.com/khanhlinh-jnf/Ares-Maze-Solver.git
```

Install the required dependencies, specifically Pygame, in order to execute the program:
```bash
pip install pygame
```

Execute the program and begin using the application:
```bash
py main.py
```
or
```bash
python main.py
```

You can also refer to the accompanying video for a demonstration of how the game runs and read the report for a detailed explanation of the project.
