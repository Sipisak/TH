import sys
import random
import networkx as nx
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                            QHBoxLayout, QWidget, QLabel, QFrame)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class StrategicNetwork(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Strategic Network Simulation")
        self.setGeometry(100, 100, 1000, 700)
        
        self.net_type = "small_world"
        self.size = 30
        self.avg_degree = 5
        self.rounds = 10
        self.current_round = 0
        self.graph = None
        self.strategies = None
        self.colors = {"rock": "gray", "scissors": "green", "paper": "blue"}
        self.strategy_history = []  # To track strategy distribution over time

        self.initUI()
        self.run_simulation()
    
    def initUI(self):
        main_layout = QHBoxLayout()
        
        # Left panel for network visualization
        left_panel = QVBoxLayout()
        self.network_figure = plt.figure(figsize=(6, 5))
        self.network_canvas = FigureCanvas(self.network_figure)
        left_panel.addWidget(self.network_canvas)
        
        # Right panel for distribution visualization and controls
        right_panel = QVBoxLayout()
        
        # Add parameters display panel
        params_frame = QFrame()
        params_frame.setFrameShape(QFrame.StyledPanel)
        params_frame.setLineWidth(1)
        params_layout = QVBoxLayout(params_frame)
        
        self.net_type_label = QLabel("Network Type: " + self.net_type)
        self.net_type_label.setAlignment(Qt.AlignCenter)
        self.size_label = QLabel(f"Network Size: {self.size} nodes")
        self.size_label.setAlignment(Qt.AlignCenter)
        self.avg_degree_label = QLabel(f"Average Degree: {self.avg_degree}")
        self.avg_degree_label.setAlignment(Qt.AlignCenter)
        self.round_label = QLabel(f"Current Round: 0/{self.rounds}")
        self.round_label.setAlignment(Qt.AlignCenter)
        
        params_layout.addWidget(self.net_type_label)
        params_layout.addWidget(self.size_label)
        params_layout.addWidget(self.avg_degree_label)
        params_layout.addWidget(self.round_label)
        
        # Add distribution visualization
        self.dist_figure = plt.figure(figsize=(5, 4))
        self.dist_canvas = FigureCanvas(self.dist_figure)
        
        right_panel.addWidget(params_frame)
        right_panel.addWidget(self.dist_canvas, 1)  # Give it more stretch
        
        # Control buttons at the bottom
        button_layout = QHBoxLayout()
        
        self.button_run = QPushButton("Run Simulation")
        self.button_run.clicked.connect(self.run_simulation)
        
        self.button_step = QPushButton("Step Simulation")
        self.button_step.clicked.connect(self.step_simulation)
        
        self.button_increase_size = QPushButton("Increase Size")
        self.button_increase_size.clicked.connect(self.increase_size)
        
        self.button_decrease_size = QPushButton("Decrease Size")
        self.button_decrease_size.clicked.connect(self.decrease_size)
        
        self.button_change_net = QPushButton("Change Network Type")
        self.button_change_net.clicked.connect(self.change_network)
        
        button_layout.addWidget(self.button_run)
        button_layout.addWidget(self.button_step)
        button_layout.addWidget(self.button_increase_size)
        button_layout.addWidget(self.button_decrease_size)
        button_layout.addWidget(self.button_change_net)
        
        # Add controls to right panel
        right_panel.addLayout(button_layout)
        
        # Combine left and right panels
        main_layout.addLayout(left_panel, 3)
        main_layout.addLayout(right_panel, 2)
        
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
    
    def update_parameter_display(self):
        """Update the parameter display labels"""
        self.net_type_label.setText("Network Type: " + self.net_type)
        self.size_label.setText(f"Network Size: {self.size} nodes")
        self.avg_degree_label.setText(f"Average Degree: {self.avg_degree}")
        self.round_label.setText(f"Current Round: {self.current_round}/{self.rounds}")
    
    def run_simulation(self):
        self.initialize_network()
        self.initialize_strategies()
        self.strategy_history = []
        self.current_round = 0
        self.record_strategy_counts()
        
        for _ in range(self.rounds):
            self.update_strategies()
            self.current_round += 1
            self.record_strategy_counts()
            
        self.update_parameter_display()
        self.visualize_network()
        self.visualize_distribution()
    
    def step_simulation(self):
        # If no simulation has been run, initialize one
        if self.graph is None or self.strategies is None:
            self.initialize_network()
            self.initialize_strategies()
            self.strategy_history = []
            self.current_round = 0
            self.record_strategy_counts()
        
        # Only proceed if we haven't reached the max rounds
        if self.current_round < self.rounds:
            self.update_strategies()
            self.current_round += 1
            self.record_strategy_counts()
            self.update_parameter_display()
            self.visualize_network()
            self.visualize_distribution()
        else:
            # Optionally reset and start over
            self.current_round = 0
            self.record_strategy_counts()
            self.update_parameter_display()
    
    def record_strategy_counts(self):
        if self.strategies is None:
            return
            
        counts = {"rock": 0, "scissors": 0, "paper": 0}
        for strategy in self.strategies.values():
            counts[strategy] += 1
        self.strategy_history.append(counts)
    
    def initialize_network(self):
        if self.net_type == "random":
            self.graph = nx.erdos_renyi_graph(self.size, p=self.avg_degree / (self.size - 1))
        elif self.net_type == "small_world":
            self.graph = nx.watts_strogatz_graph(self.size, k=min(self.avg_degree, self.size-1), p=0.2)
        elif self.net_type == "preferential_attachment":
            self.graph = nx.barabasi_albert_graph(self.size, m=max(1, min(self.avg_degree // 2, self.size-1)))
    
    def initialize_strategies(self):
        self.strategies = {node: random.choice(["rock", "scissors", "paper"]) for node in self.graph.nodes}
    
    def play_round(self, player1, player2):
        if player1 == player2:
            return 0  # Draw
        elif (player1 == "rock" and player2 == "scissors") or \
             (player1 == "scissors" and player2 == "paper") or \
             (player1 == "paper" and player2 == "rock"):
            return 1  # Player 1 wins
        else:
            return -1  # Player 2 wins
    
    def update_strategies(self):
        new_strategies = self.strategies.copy()
        for node in self.graph.nodes:
            neighbors = list(self.graph.neighbors(node))
            if neighbors:
                opponent = random.choice(neighbors)
                result = self.play_round(self.strategies[node], self.strategies[opponent])
                if result == -1:
                    new_strategies[node] = self.strategies[opponent]
        self.strategies = new_strategies
    
    def visualize_network(self):
        self.network_figure.clear()
        ax = self.network_figure.add_subplot(111)
        pos = nx.spring_layout(self.graph, seed=42)  # Fixed seed for consistent layout
        node_colors = [self.colors[self.strategies[node]] for node in self.graph.nodes]
        nx.draw(self.graph, pos, node_color=node_colors, with_labels=True, ax=ax)
        self.network_figure.suptitle(f"Network: {self.net_type}", fontsize=12)
        self.network_canvas.draw()
    
    def visualize_distribution(self):
        self.dist_figure.clear()
        ax = self.dist_figure.add_subplot(111)
        
        if not self.strategy_history:
            self.dist_canvas.draw()
            return
            
        rounds = list(range(len(self.strategy_history)))
        rock_counts = [counts["rock"] for counts in self.strategy_history]
        paper_counts = [counts["paper"] for counts in self.strategy_history]
        scissors_counts = [counts["scissors"] for counts in self.strategy_history]
        
        ax.plot(rounds, rock_counts, 'o-', color=self.colors["rock"], label="Rock")
        ax.plot(rounds, scissors_counts, 'o-', color=self.colors["scissors"], label="Scissors")
        ax.plot(rounds, paper_counts, 'o-', color=self.colors["paper"], label="Paper")
        
        ax.set_xlabel('Round')
        ax.set_ylabel('Count')
        ax.set_title('Strategy Distribution Over Time')
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Set y-axis to show integer values only
        ax.set_yticks(range(0, self.size + 1, max(1, self.size // 10)))
        
        self.dist_canvas.draw()
    
    def increase_size(self):
        self.size += 10
        self.run_simulation()
    
    def decrease_size(self):
        if self.size > 10:
            self.size -= 10
            self.run_simulation()
    
    def change_network(self):
        net_types = ["random", "small_world", "preferential_attachment"]
        self.net_type = net_types[(net_types.index(self.net_type) + 1) % 3]
        self.run_simulation()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StrategicNetwork()
    window.show()
    sys.exit(app.exec_())