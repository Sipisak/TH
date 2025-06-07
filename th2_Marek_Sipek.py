import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Set, Any, Optional
import random

@dataclass
class Student:
    name: str
    preferences: List[str]
    score: int
    
    def __str__(self) -> str:
        return f"{self.name} (Score: {self.score}): {', '.join(self.preferences)}"

@dataclass
class School:
    name: str
    capacity: int
    accepted: List[Tuple[str, int]] = field(default_factory=list)
    
    def __str__(self) -> str:
        return f"{self.name} (Capacity: {self.capacity})"
    
    def is_full(self) -> bool:
        return len(self.accepted) >= self.capacity

class CollegeAdmissionsApp:
    """Main application class for the College Admissions Matcher"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("College Admissions Matcher")
        self.root.geometry("1200x800")
        
        self.students: List[Student] = []
        self.schools: Dict[str, School] = {}
        
        self.setup_ui()
    
    def setup_ui(self):
        """Initialize the main UI components"""
        # Create notebook for tabbed interface
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.input_frame = ttk.Frame(self.notebook)
        self.visualization_frame = ttk.Frame(self.notebook)
        self.results_frame = ttk.Frame(self.notebook)
        
        self.notebook.add(self.input_frame, text="Input Data")
        self.notebook.add(self.visualization_frame, text="Visualization")
        self.notebook.add(self.results_frame, text="Results")
        
        # Setup tabs
        self.setup_input_tab()
        self.setup_visualization_tab()
        self.setup_results_tab()
    
    
    def _create_labeled_entry(self, parent, label_text, row, column, width=20):
        ttk.Label(parent, text=label_text).grid(row=row, column=column, padx=5, pady=5)
        entry = ttk.Entry(parent, width=width)
        entry.grid(row=row, column=column+1, padx=5, pady=5)
        return entry
    
    def _create_button(self, parent, text, command, row, column, columnspan=2):
        button = ttk.Button(parent, text=text, command=command)
        button.grid(row=row, column=column, columnspan=columnspan, padx=5, pady=5)
        return button
    
    
    
    def setup_input_tab(self):
        """Setup the input tab with student and school data entry forms"""
        # Create frame for students input
        students_frame = ttk.LabelFrame(self.input_frame, text="Students")
        students_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.student_name = self._create_labeled_entry(students_frame, "Name:", 0, 0)
        self.student_score = self._create_labeled_entry(students_frame, "Score:", 1, 0)
        self.student_preferences = self._create_labeled_entry(students_frame, "Preferences (comma separated):", 2, 0, width=40)
        self._create_button(students_frame, "Add Student", self.add_student, 3, 0)
        
        # Create frame for schools input
        schools_frame = ttk.LabelFrame(self.input_frame, text="Schools")
        schools_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        self.school_name = self._create_labeled_entry(schools_frame, "Name:", 0, 0)
        self.school_capacity = self._create_labeled_entry(schools_frame, "Capacity:", 1, 0)
        self._create_button(schools_frame, "Add School", self.add_school, 2, 0)
        
        # Create frame for current data
        data_frame = ttk.LabelFrame(self.input_frame, text="Current Data")
        data_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        self.data_text = scrolledtext.ScrolledText(data_frame, width=80, height=15)
        self.data_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Control buttons
        control_frame = ttk.Frame(self.input_frame)
        control_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, expand=True)
        
        buttons = [
            ("Run Matching", self.run_matching),
            ("Load Sample Data", self.load_sample_data),
            ("Clear All", self.clear_all),
            ("Analyze Score Impact", self.explore_score_sensitivity),
            ("Generate Random Data", self.generate_random_data),
            ("Animate Algorithm", self.animate_matching)
        ]
        
        for i, (text, command) in enumerate(buttons):
            ttk.Button(button_frame, text=text, command=command).grid(
                row=0, column=i, padx=5, pady=5
            )
        
        # Configure grid weights
        self.input_frame.columnconfigure(0, weight=1)
        self.input_frame.columnconfigure(1, weight=1)
        self.input_frame.rowconfigure(1, weight=1)
    
    def setup_visualization_tab(self):
        """Setup the visualization tab with treeviews for students and schools"""
        # Create a grid layout with two columns
        self.visualization_frame.columnconfigure(0, weight=1)
        self.visualization_frame.columnconfigure(1, weight=1)
        self.visualization_frame.rowconfigure(0, weight=1)
        
        # Frame for students visualization
        students_viz_frame = ttk.LabelFrame(self.visualization_frame, text="Students")
        students_viz_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Create a Treeview for students
        self.students_tree = self._create_treeview(
            students_viz_frame, 
            columns=("Score", "Preferences"),
            headings=["Score", "Preferences"],
            widths=[50, 300]
        )
        
        # Frame for schools visualization
        schools_viz_frame = ttk.LabelFrame(self.visualization_frame, text="Schools")
        schools_viz_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # Create a Treeview for schools
        self.schools_tree = self._create_treeview(
            schools_viz_frame, 
            columns=("Capacity",),
            headings=["Capacity"],
            widths=[80]
        )
    
    def setup_results_tab(self):
        """Setup the results tab with matching visualization"""
        # Create a vertical paned window
        results_paned = ttk.PanedWindow(self.results_frame, orient=tk.VERTICAL)
        results_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top frame for matching results in table form
        table_frame = ttk.LabelFrame(results_paned, text="Matching Results")
        results_paned.add(table_frame, weight=1)
        
        # Create a Treeview for matching results with scrollbar
        self.results_tree = ttk.Treeview(table_frame, columns=("Students",), show="headings")
        self.results_tree.heading("Students", text="Assigned Students")
        self.results_tree.column("Students", width=400)
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar.set)
        
        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bottom section split into visualization and details
        bottom_frame = ttk.Frame(results_paned)
        results_paned.add(bottom_frame, weight=1)
        
        # Create horizontal paned window for bottom section
        bottom_paned = ttk.PanedWindow(bottom_frame, orient=tk.HORIZONTAL)
        bottom_paned.pack(fill=tk.BOTH, expand=True)
        
        # Visual representation frame (left side of bottom)
        visual_frame = ttk.LabelFrame(bottom_paned, text="Visual Matching")
        bottom_paned.add(visual_frame, weight=2)
        
        # Canvas for drawing the visualization
        self.visual_canvas = tk.Canvas(visual_frame, bg="white")
        self.visual_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Text output for detailed results (right side of bottom)
        output_frame = ttk.LabelFrame(bottom_paned, text="Details")
        bottom_paned.add(output_frame, weight=1)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, width=40, height=15)
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def _create_treeview(self, parent, columns, headings, widths):
        """Create and configure a Treeview with scrollbar"""
        treeview = ttk.Treeview(parent, columns=columns, show="headings")
        
        for col, heading, width in zip(columns, headings, widths):
            treeview.heading(col, text=heading)
            treeview.column(col, width=width)
            
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=treeview.yview)
        treeview.configure(yscrollcommand=scrollbar.set)
        
        treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        return treeview
    
    def _validate_student_input(self) -> Optional[Tuple[str, List[str], int]]:
        """Validate student input and return processed data if valid"""
        name = self.student_name.get().strip()
        score_str = self.student_score.get().strip()
        preferences = [p.strip() for p in self.student_preferences.get().split(',') if p.strip()]
        
        if not name or not preferences:
            messagebox.showerror("Error", "Name and preferences are required!")
            return None
            
        try:
            score = int(score_str)
        except ValueError:
            messagebox.showerror("Error", "Score must be a number!")
            return None
            
        # Check for duplicates
        if any(student.name == name for student in self.students):
            messagebox.showerror("Error", f"Student {name} already exists!")
            return None
            
        return name, preferences, score

    def _validate_school_input(self) -> Optional[Tuple[str, int]]:
        """Validate school input and return processed data if valid"""
        name = self.school_name.get().strip()
        capacity_str = self.school_capacity.get().strip()
        
        if not name:
            messagebox.showerror("Error", "School name is required!")
            return None
            
        try:
            capacity = int(capacity_str)
            if capacity <= 0:
                messagebox.showerror("Error", "Capacity must be positive!")
                return None
        except ValueError:
            messagebox.showerror("Error", "Capacity must be a number!")
            return None
            
        # Check for duplicates
        if name in self.schools:
            messagebox.showerror("Error", f"School {name} already exists!")
            return None
            
        return name, capacity
    
    def add_student(self):
        """Add a student from input fields to the data model"""
        result = self._validate_student_input()
        if result is None:
            return
            
        name, preferences, score = result
        student = Student(name, preferences, score)
        self.students.append(student)
        
        # Clear the entries
        self._clear_student_inputs()
        
        # Update displays
        self.update_data_display()
        self.update_visualization()

    def add_school(self):
        """Add a school from input fields to the data model"""
        result = self._validate_school_input()
        if result is None:
            return
            
        name, capacity = result
        school = School(name, capacity)
        self.schools[name] = school
        
        # Clear the entries
        self._clear_school_inputs()
        
        # Update displays
        self.update_data_display()
        self.update_visualization()
    
    def update_data_display(self):
        """Update the text display with current students and schools"""
        self.data_text.delete(1.0, tk.END)
        
        # Display students
        self.data_text.insert(tk.END, "STUDENTS:\n")
        for student in self.students:
            self.data_text.insert(tk.END, f"{student}\n")
        
        self.data_text.insert(tk.END, "\nSCHOOLS:\n")
        for school in self.schools.values():
            self.data_text.insert(tk.END, f"{school}\n")
    
    def update_visualization(self):
        """Update the tree views with current students and schools"""
        # Clear existing items
        self._clear_treeview(self.students_tree)
        self._clear_treeview(self.schools_tree)
        
        # Add students to the Treeview
        for student in self.students:
            self.students_tree.insert(
                "", "end", 
                text=student.name, 
                values=(student.score, ", ".join(student.preferences)), 
                iid=student.name
            )
        
        # Add schools to the Treeview
        for name, school in self.schools.items():
            self.schools_tree.insert(
                "", "end", 
                text=name, 
                values=(school.capacity,), 
                iid=name
            )
    
    def _clear_treeview(self, treeview):
        """Helper method to clear a treeview"""
        for item in treeview.get_children():
            treeview.delete(item)
    
    def _clear_student_inputs(self):
        """Clear student input fields"""
        self.student_name.delete(0, tk.END)
        self.student_score.delete(0, tk.END)
        self.student_preferences.delete(0, tk.END)
    
    def _clear_school_inputs(self):
        """Clear school input fields"""
        self.school_name.delete(0, tk.END)
        self.school_capacity.delete(0, tk.END)
    
    def run_matching(self):
        """Run the matching algorithm and display results"""
        if not self.students or not self.schools:
            messagebox.showerror("Error", "No students or schools available!")
            return

        matches = self.gale_shapley_matching()
        
        # Clear existing results
        self._clear_treeview(self.results_tree)
        self.output_text.delete(1.0, tk.END)
        
        # Add results to the Treeview and text output
        for school_name, student_names in matches.items():
            self.results_tree.insert(
                "", "end", 
                text=school_name, 
                values=(", ".join(student_names),), 
                iid=school_name
            )
            self.output_text.insert(tk.END, f"{school_name}: {', '.join(student_names)}\n")
        
        # Visualize the matching
        self.visualize_matching(matches)
        
        # Switch to results tab
        self.notebook.select(self.results_frame)
    
    def gale_shapley_matching(self):
        """Implementation of the Gale-Shapley algorithm for stable matching"""
        # Convert students to a dictionary for easier access
        student_dict = {student.name: {"prefs": student.preferences, "score": student.score} 
                       for student in self.students}
        
        # Initialize schools with empty accepted lists
        schools_dict = {name: {"capacity": school.capacity, "accepted": []} 
                       for name, school in self.schools.items()}
        
        # Track unmatched students and their preference index
        unmatched = [student.name for student in self.students]
        pref_index = {student.name: 0 for student in self.students}
        
        # Run the algorithm until no unmatched students remain or all preferences exhausted
        while unmatched:
            student = unmatched.pop(0)
            
            # Check if student has any remaining preferences
            student_prefs = student_dict[student]["prefs"]
            if pref_index[student] >= len(student_prefs):
                continue
                
            # Get student's next preferred school
            school = student_prefs[pref_index[student]]
            pref_index[student] += 1
            
            # Skip if school doesn't exist
            if school not in schools_dict:
                unmatched.append(student)
                continue
                
            school_data = schools_dict[school]
            student_score = student_dict[student]["score"]
            
            # Case 1: School has space - accept student
            if len(school_data["accepted"]) < school_data["capacity"]:
                school_data["accepted"].append((student, student_score))
            else:
                # Case 2: School is full - compare with lowest scoring accepted student
                current = sorted(school_data["accepted"], key=lambda x: x[1])
                if student_score > current[0][1]:
                    # Replace lowest scoring student
                    rejected = current[0][0]
                    school_data["accepted"].remove(current[0])
                    school_data["accepted"].append((student, student_score))
                    unmatched.append(rejected)
                else:
                    # Student rejected - try next preference
                    unmatched.append(student)
        
        # Format results - sort students by score within each school
        return {
            school: [s[0] for s in sorted(data["accepted"], key=lambda x: x[1], reverse=True)]
            for school, data in schools_dict.items()
        }
    
    def visualize_matching(self, matches):
        """Visualize the matching results on canvas"""
        self.visual_canvas.delete("all")
        
        # Get dimensions
        canvas_width = self.visual_canvas.winfo_width()
        canvas_height = self.visual_canvas.winfo_height()
        
        # If canvas is not yet properly sized, try again after a short delay
        if canvas_width < 50 or canvas_height < 50:
            self.visual_canvas.after(100, lambda: self.visualize_matching(matches))
            return
        
        schools = list(matches.keys())
        all_students = list(set(sum([matches[s] for s in schools], [])))
        
        # Calculate positions
        school_x = canvas_width // 4
        student_x = 3 * canvas_width // 4
        
        # Draw elements and connections
        school_positions = self._draw_schools(schools, school_x, canvas_height)
        student_positions = self._draw_students(all_students, student_x, canvas_height)
        self._draw_connections(matches, school_positions, student_positions)

    def _draw_schools(self, schools, x_pos, canvas_height):
        """Draw school nodes on the canvas"""
        school_color = "#3498db"  # Blue
        school_positions = {}
        school_spacing = canvas_height // (len(schools) + 1)
        
        for i, school in enumerate(schools):
            y = (i + 1) * school_spacing
            school_positions[school] = (x_pos, y)
            
            # Draw school node
            self.visual_canvas.create_oval(
                x_pos - 20, y - 20, 
                x_pos + 20, y + 20, 
                fill=school_color, outline="black"
            )
            # Draw school name
            self.visual_canvas.create_text(
                x_pos, y, 
                text=school, 
                font=("Arial", 10, "bold")
            )
            # Draw capacity
            capacity = self.schools[school].capacity
            self.visual_canvas.create_text(
                x_pos, y + 25, 
                text=f"Capacity: {capacity}", 
                font=("Arial", 8)
            )
        
        return school_positions

    def _draw_students(self, students, x_pos, canvas_height):
        """Draw student nodes on the canvas"""
        student_color = "#2ecc71"  # Green
        student_positions = {}
        student_spacing = canvas_height // (len(students) + 1)
        
        for i, student_name in enumerate(students):
            y = (i + 1) * student_spacing
            student_positions[student_name] = (x_pos, y)
            
            # Draw student node
            self.visual_canvas.create_oval(
                x_pos - 15, y - 15, 
                x_pos + 15, y + 15, 
                fill=student_color, outline="black"
            )
            # Draw student name
            self.visual_canvas.create_text(
                x_pos, y, 
                text=student_name, 
                font=("Arial", 9, "bold")
            )
            
            # Find student score
            for student in self.students:
                if student.name == student_name:
                    self.visual_canvas.create_text(
                        x_pos, y + 20, 
                        text=f"Score: {student.score}", 
                        font=("Arial", 8)
                    )
                    break
        
        return student_positions

    def _draw_connections(self, matches, school_positions, student_positions):
        """Draw connection lines between matched schools and students"""
        line_color = "#e74c3c"  # Red
        
        for school, students in matches.items():
            sx, sy = school_positions[school]
            for student in students:
                if student in student_positions:  # Ensure the student position exists
                    tx, ty = student_positions[student]
                    
                    # Draw arrow from student to school
                    self.visual_canvas.create_line(
                        sx + 20, sy, tx - 15, ty, 
                        arrow="first", width=1.5, 
                        fill=line_color
                    )
    
    def load_sample_data(self):
        """Load sample students and schools data"""
        # Clear existing data
        self._clear_data()
        
        # Add sample students
        sample_students = [
            Student("Alice", ["MIT", "Stanford", "Harvard"], 95),
            Student("Bob", ["Harvard", "MIT", "Stanford"], 88),
            Student("Charlie", ["Stanford", "Harvard", "MIT"], 92),
            Student("David", ["MIT", "Harvard", "Stanford"], 85),
            Student("Eva", ["Harvard", "Stanford", "MIT"], 90),
            Student("Frank", ["Stanford", "MIT", "Harvard"], 87),
            Student("Grace", ["MIT", "Stanford", "Harvard"], 93),
            Student("Hannah", ["Harvard", "Stanford", "MIT"], 89)
        ]
        
        self.students = sample_students
        
        # Add sample schools
        self.schools = {
            "MIT": School("MIT", 3),
            "Stanford": School("Stanford", 2),
            "Harvard": School("Harvard", 2)
        }
        
        # Update displays
        self.update_data_display()
        self.update_visualization()
        
        messagebox.showinfo("Sample Data", "Sample data loaded successfully!")
    
    def clear_all(self):
        """Clear all data and input fields"""
        self._clear_data()
        self._clear_student_inputs()
        self._clear_school_inputs()
        
        # Clear displays
        self.data_text.delete(1.0, tk.END)
        self._clear_treeview(self.students_tree)
        self._clear_treeview(self.schools_tree)
        self._clear_treeview(self.results_tree)
        self.output_text.delete(1.0, tk.END)
        
        # Clear visualization
        if hasattr(self, 'visual_canvas'):
            self.visual_canvas.delete("all")
            
        messagebox.showinfo("Clear Data", "All data has been cleared.")
    
    def _clear_data(self):
        """Clear the data model"""
        self.students = []
        self.schools = {}
    
    def generate_random_data(self):
        """Generate random students and schools data with realistic values"""
        try:
            from tkinter import simpledialog
        except ImportError:
            messagebox.showerror("Error", "Required modules not available")
            return
        
        # Ask for number of students and schools
        num_students = simpledialog.askinteger("Input", "Number of students to generate:",
                                              minvalue=2, maxvalue=100)
        if not num_students:
            return
            
        num_schools = simpledialog.askinteger("Input", "Number of schools to generate:",
                                             minvalue=2, maxvalue=20)
        if not num_schools:
            return
        
        # Clear existing data
        self._clear_data()
        
        # Generate school names and create schools
        school_names = self._generate_random_school_names(num_schools, num_students)
        
        # Generate students
        self.students = self._generate_random_students(num_students, school_names)
        
        # Update displays
        self.update_data_display()
        self.update_visualization()
        
        messagebox.showinfo("Random Data", "Random data generated successfully!")
    
    def _generate_random_school_names(self, num_schools, num_students):
        """Generate random school names and create School objects"""
        school_prefixes = [
            "North", "South", "East", "West", "Central", "Pacific", 
            "Atlantic", "Global", "National", "International", "City",
            "Metro", "Bay", "River", "Mountain", "Valley", "Lake"
        ]
        
        school_suffixes = [
            "University", "College", "Institute", "Academy", "School"
        ]
        
        school_names = []
        
        for i in range(num_schools):
            prefix = random.choice(school_prefixes)
            suffix = random.choice(school_suffixes)
            name = f"{prefix} {suffix}"
            
            # Ensure unique name
            attempt = 1
            while name in self.schools:
                name = f"{prefix} {suffix} {attempt}"
                attempt += 1
            
            capacity = random.randint(1, max(2, num_students // 3))
            self.schools[name] = School(name, capacity)
            school_names.append(name)
            
        return school_names
    
    def _generate_random_students(self, num_students, school_names):
        """Generate random Student objects"""
        first_names = [
            "Alex", "Blake", "Casey", "Drew", "Ellis", "Francis", "Gray", "Harper",
            "Indigo", "Jordan", "Kennedy", "Logan", "Morgan", "Noah", "Parker", "Quinn",
            "Riley", "Sam", "Taylor", "Valerie", "Wyatt", "Xavier", "Yael", "Zion"
        ]
        
        last_names = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Garcia",
            "Rodriguez", "Wilson", "Martinez", "Anderson", "Taylor"
        ]
        
        students = []
        
        for i in range(num_students):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            name = f"{first_name} {last_name}"
            
            # Ensure unique name
            attempt = 1
            while any(student.name == name for student in students):
                name = f"{first_name} {last_name} {attempt}"
                attempt += 1
            
            score = random.randint(50, 100)
            num_prefs = min(len(school_names), random.randint(1, 5))
            preferences = random.sample(school_names, k=num_prefs)
            
            students.append(Student(name, preferences, score))
            
        return students
    
    def explore_score_sensitivity(self):
        """Analyze how changes in student scores affect the matching outcome"""
        if not self.students or not self.schools:
            messagebox.showerror("Error", "No students or schools available!")
            return
        
    
        try:
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            import numpy as np
        except ImportError:
            messagebox.showerror("Error", "Please install matplotlib: pip install matplotlib")
            return
        
        # Create analysis window and setup UI
        analysis_window = tk.Toplevel(self.root)
        analysis_window.title("Score Sensitivity Analysis")
        analysis_window.geometry("1000x700")
        
        # Setup tabbed interface for different analysis views
        analysis_notebook = ttk.Notebook(analysis_window)
        analysis_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        text_tab = ttk.Frame(analysis_notebook)
        chart_tab = ttk.Frame(analysis_notebook)
        
        analysis_notebook.add(text_tab, text="Text Analysis")
        analysis_notebook.add(chart_tab, text="Charts")
        
        # Get original matching for comparison
        original_matches = self.gale_shapley_matching()
        
        # Setup text analysis tab
        self._setup_text_analysis_tab(text_tab, original_matches)
        
        # Setup chart analysis tab
        self._setup_chart_analysis_tab(chart_tab, original_matches)
    
    def _setup_text_analysis_tab(self, parent, original_matches):
        """Setup the text-based sensitivity analysis interface"""
        # Create a frame for controls
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Score adjustment slider
        ttk.Label(control_frame, text="Score Adjustment Factor:").grid(row=0, column=0, padx=5, pady=5)
        score_factor = ttk.Scale(control_frame, from_=0.5, to=1.5, orient=tk.HORIZONTAL, length=200)
        score_factor.set(1.0)  # Default - no change
        score_factor.grid(row=0, column=1, padx=5, pady=5)
        
        # Display current factor value
        factor_label = ttk.Label(control_frame, text="1.00")
        factor_label.grid(row=0, column=2, padx=5, pady=5)
        
        # Create frames for results comparison
        results_frame = ttk.Frame(parent)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Split into original and adjusted results
        original_frame = ttk.LabelFrame(results_frame, text="Original Matching")
        original_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        adjusted_frame = ttk.LabelFrame(results_frame, text="Adjusted Matching")
        adjusted_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        
        # Text widgets for displaying results
        original_text = scrolledtext.ScrolledText(original_frame, width=30, height=20)
        original_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        adjusted_text = scrolledtext.ScrolledText(adjusted_frame, width=30, height=20)
        adjusted_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame for changes
        changes_frame = ttk.LabelFrame(parent, text="Changes in Assignment")
        changes_frame.pack(fill=tk.X, padx=10, pady=10)
        
        changes_text = scrolledtext.ScrolledText(changes_frame, width=70, height=10)
        changes_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Display original matching
        original_text.delete(1.0, tk.END)
        for school, students in original_matches.items():
            original_text.insert(tk.END, f"{school}: {', '.join(students)}\n")
        
        # Configure grid weights for the results frame
        results_frame.columnconfigure(0, weight=1)
        results_frame.columnconfigure(1, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # Function to update analysis based on slider movement
        def update_text_analysis(*args):
            # Get current factor
            factor = score_factor.get()
            factor_label.config(text=f"{factor:.2f}")
            
            # Run matching with adjusted scores
            adjusted_matches = self._run_adjusted_matching(factor)
            
            # Display adjusted results
            adjusted_text.delete(1.0, tk.END)
            for school, students in adjusted_matches.items():
                adjusted_text.insert(tk.END, f"{school}: {', '.join(students)}\n")
            
            # Find and display changes
            changes_text.delete(1.0, tk.END)
            self._display_matching_changes(changes_text, original_matches, adjusted_matches)
        
        # Bind the scale to update function
        score_factor.bind("<ButtonRelease-1>", update_text_analysis)
        
        # Initial analysis
        update_text_analysis()
    
    def _setup_chart_analysis_tab(self, parent, original_matches):
        """Setup the chart-based sensitivity analysis interface"""
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        import numpy as np
        
        chart_control_frame = ttk.Frame(parent)
        chart_control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Create slider for chart tab
        ttk.Label(chart_control_frame, text="Score Adjustment Range:").pack(side=tk.LEFT, padx=5, pady=5)
        
        # Create a figure for charts
        fig = plt.Figure(figsize=(10, 8), dpi=100)
        
        # Create subplots
        ax1 = fig.add_subplot(221)  # School allocation changes
        ax2 = fig.add_subplot(222)  # Student scores distribution
        ax3 = fig.add_subplot(212)  # Stability analysis
        
        # Create canvas for matplotlib charts
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Prepare data for initial plots
        student_names = [student.name for student in self.students]
        student_scores = [student.score for student in self.students]
        school_names = list(self.schools.keys())
        
        # Title for the charts
        fig.suptitle("Score Sensitivity Analysis", fontsize=16)
        
        # Store factors and changes for stability analysis
        factors_to_analyze = np.linspace(0.5, 1.5, 11)  # 0.5, 0.6, ... 1.5
        
        def update_charts():
            # Clear previous plots
            for ax in [ax1, ax2, ax3]:
                ax.clear()
                
            # Calculate changes at different factor levels
            change_counts = []
            school_allocations = {school: [] for school in self.schools}
                
            for factor in factors_to_analyze:
                # Run matching with adjusted scores
                adjusted_matches = self._run_adjusted_matching(factor)
                
                # Count changes from original
                changes = self._count_matching_changes(original_matches, adjusted_matches)
                change_counts.append(changes)
                
                # Store school allocation counts
                for school in self.schools:
                    if school in adjusted_matches:
                        school_allocations[school].append(len(adjusted_matches[school]))
                    else:
                        school_allocations[school].append(0)
            
            # Plot 1: School allocation changes
            for school, counts in school_allocations.items():
                ax1.plot(factors_to_analyze, counts, marker='o', label=school)
            ax1.set_xlabel('Score Factor')
            ax1.set_ylabel('Students Allocated')
            ax1.set_title('School Allocations')
            ax1.legend()
            ax1.grid(True)
            
            # Plot 2: Student scores distribution
            sorted_indices = np.argsort(student_scores)
            sorted_names = [student_names[i] for i in sorted_indices]
            sorted_scores = [student_scores[i] for i in sorted_indices]
            
            ax2.bar(sorted_names, sorted_scores, color='skyblue')
            ax2.set_title('Student Scores Distribution')
            ax2.set_ylabel('Score')
            ax2.tick_params(axis='x', rotation=45)
            
            # Plot 3: Stability analysis - changes vs factor
            ax3.plot(factors_to_analyze, change_counts, 'ro-', linewidth=2)
            ax3.set_title('Matching Stability Analysis')
            ax3.set_xlabel('Score Factor')
            ax3.set_ylabel('Number of Changes')
            ax3.grid(True)
            
            # Refresh canvas
            fig.tight_layout(rect=[0, 0, 1, 0.95])  # Make room for suptitle
            canvas.draw()
        
        # Set up analyze button for charts
        ttk.Button(chart_control_frame, text="Analyze Full Range", 
                  command=update_charts).pack(side=tk.LEFT, padx=20)
        
        # Initial chart analysis
        update_charts()
    
    def _run_adjusted_matching(self, factor):
        """Run matching algorithm with adjusted student scores"""
        # Create temporary adjusted students list
        adjusted_students = []
        for student in self.students:
            adjusted_score = int(student.score * factor)
            adjusted_students.append(Student(student.name, student.preferences, adjusted_score))
        
        # Save original students temporarily
        original_students = self.students
        
        # Replace with adjusted students and run matching
        self.students = adjusted_students
        adjusted_matches = self.gale_shapley_matching()
        
        # Restore original students
        self.students = original_students
        
        return adjusted_matches
    
    def _display_matching_changes(self, text_widget, original_matches, adjusted_matches):
        """Display changes between two matchings in a text widget"""
        changes_found = False
        
        for school in set(original_matches.keys()) | set(adjusted_matches.keys()):
            original_set = set(original_matches.get(school, []))
            adjusted_set = set(adjusted_matches.get(school, []))
            
            if original_set != adjusted_set:
                changes_found = True
                text_widget.insert(tk.END, f"Changes for {school}:\n")
                
                # Students who were removed
                removed = original_set - adjusted_set
                if removed:
                    text_widget.insert(tk.END, f"  Removed: {', '.join(removed)}\n")
                
                # Students who were added
                added = adjusted_set - original_set
                if added:
                    text_widget.insert(tk.END, f"  Added: {', '.join(added)}\n")
                
                text_widget.insert(tk.END, "\n")
        
        if not changes_found:
            text_widget.insert(tk.END, "No changes in assignments with current factor.")
    
    def _count_matching_changes(self, original_matches, adjusted_matches):
        """Count the number of changes between two matchings"""
        changes = 0
        
        for school in set(original_matches.keys()) | set(adjusted_matches.keys()):
            original_set = set(original_matches.get(school, []))
            adjusted_set = set(adjusted_matches.get(school, []))
            changes += len(original_set.symmetric_difference(adjusted_set))
            
        return changes
    #endregion

    #region Animation Methods
    def animate_matching(self):
        """Run the matching algorithm with animation to show each step"""
        if not self.students or not self.schools:
            messagebox.showerror("Error", "No students or schools available!")
            return

        # Create animation window
        anim_window = tk.Toplevel(self.root)
        anim_window.title("Algorithm Animation")
        anim_window.geometry("1000x700")
        
        # Create frames
        control_frame = ttk.Frame(anim_window)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Canvas for animation
        canvas_frame = ttk.Frame(anim_window)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        canvas = tk.Canvas(canvas_frame, bg="white")
        canvas.pack(fill=tk.BOTH, expand=True)
        
        # Status text display
        status_frame = ttk.LabelFrame(anim_window, text="Algorithm Status")
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        status_text = scrolledtext.ScrolledText(status_frame, height=8)
        status_text.pack(fill=tk.X, padx=5, pady=5)
        
        # Current state
        animation_state = {
            "running": False,
            "step": 0,
            "speed": 1.0,  # seconds between steps
            "student_dict": {},
            "schools_dict": {},
            "unmatched": [],
            "pref_index": {},
            "history": [],
            "current_student": None,
            "current_school": None
        }
        
        # Control buttons
        ttk.Button(control_frame, text="Start", 
                  command=lambda: self._animation_start(animation_state, canvas, status_text)).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="Step", 
                  command=lambda: self._animation_step(animation_state, canvas, status_text)).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="Reset", 
                  command=lambda: self._animation_reset(animation_state, canvas, status_text)).pack(side=tk.LEFT, padx=5)
        
        # Speed control
        ttk.Label(control_frame, text="Speed:").pack(side=tk.LEFT, padx=(20, 5))
        speed_scale = ttk.Scale(control_frame, from_=0.1, to=2.0, orient=tk.HORIZONTAL, length=200)
        speed_scale.set(1.0)
        speed_scale.pack(side=tk.LEFT, padx=5)
        
        def update_speed(*args):
            animation_state["speed"] = speed_scale.get()
            
        speed_scale.configure(command=update_speed)
        
        # Initialize animation
        self._animation_reset(animation_state, canvas, status_text)
        
        # Focus window
        anim_window.focus_set()

    def _animation_reset(self, state, canvas, status_text):
        """Reset animation to initial state"""
        # Stop any running animation
        state["running"] = False
        state["step"] = 0
        
        # Clear display
        canvas.delete("all")
        status_text.delete(1.0, tk.END)
        
        # Initialize algorithm state
        state["student_dict"] = {student.name: {"prefs": student.preferences, "score": student.score} 
                               for student in self.students}
        
        state["schools_dict"] = {name: {"capacity": school.capacity, "accepted": []} 
                               for name, school in self.schools.items()}
        
        state["unmatched"] = [student.name for student in self.students]
        state["pref_index"] = {student.name: 0 for student in self.students}
        state["history"] = []
        state["current_student"] = None
        state["current_school"] = None
        
        # Draw initial state
        self._draw_animation_state(state, canvas)
        
        status_text.insert(tk.END, "Algorithm initialized. Ready to start.\n")
        status_text.insert(tk.END, f"Total students: {len(self.students)}\n")
        status_text.insert(tk.END, f"Total schools: {len(self.schools)}\n")
        status_text.insert(tk.END, "Press 'Start' to run animation or 'Step' for step-by-step.\n")

    def _animation_start(self, state, canvas, status_text):
        """Start or pause continuous animation"""
        state["running"] = not state["running"]
        
        if state["running"]:
            self._animation_run_step(state, canvas, status_text)

    def _animation_step(self, state, canvas, status_text):
        """Perform a single animation step"""
        state["running"] = False
        self._animation_run_step(state, canvas, status_text)

    def _animation_run_step(self, state, canvas, status_text):
        """Execute one step of the algorithm"""
        # Check if we have unmatched students
        if not state["unmatched"]:
            status_text.insert(tk.END, "\nAlgorithm complete! All students processed.\n")
            state["running"] = False
            return
        
        # Get next student
        student = state["unmatched"].pop(0)
        state["current_student"] = student
        
        # Check if student has preferences left
        student_prefs = state["student_dict"][student]["prefs"]
        if state["pref_index"][student] >= len(student_prefs):
            status_text.insert(tk.END, f"\n{student} has no more preferences - remains unmatched.\n")
            self._draw_animation_state(state, canvas)
            
            # Schedule next step if running
            if state["running"]:
                canvas.after(int(state["speed"] * 1000), 
                            lambda: self._animation_run_step(state, canvas, status_text))
            return
        
        # Get student's next preferred school
        school = student_prefs[state["pref_index"][student]]
        state["pref_index"][student] += 1
        state["current_school"] = school
        
        status_text.insert(tk.END, f"\nStep {state['step'] + 1}: {student} applies to {school}\n")
        state["step"] += 1
        
        # Skip if school doesn't exist
        if school not in state["schools_dict"]:
            status_text.insert(tk.END, f"  School {school} doesn't exist - student tries again.\n")
            state["unmatched"].append(student)
            self._draw_animation_state(state, canvas)
            
            # Schedule next step if running
            if state["running"]:
                canvas.after(int(state["speed"] * 1000), 
                            lambda: self._animation_run_step(state, canvas, status_text))
            return
        
        # Process student application to school
        school_data = state["schools_dict"][school]
        student_score = state["student_dict"][student]["score"]
        
        # Save state for history
        state["history"].append({
            "student": student,
            "school": school,
            "action": None,
            "rejected": None
        })
        
        # Case 1: School has space - accept student
        if len(school_data["accepted"]) < school_data["capacity"]:
            school_data["accepted"].append((student, student_score))
            status_text.insert(tk.END, f"  {school} has space and accepts {student}.\n")
            state["history"][-1]["action"] = "accepted"
        else:
            # Case 2: School is full - compare with lowest scoring accepted student
            current = sorted(school_data["accepted"], key=lambda x: x[1])
            if student_score > current[0][1]:
                # Replace lowest scoring student
                rejected = current[0][0]
                school_data["accepted"].remove(current[0])
                school_data["accepted"].append((student, student_score))
                state["unmatched"].append(rejected)
                status_text.insert(tk.END, 
                                 f"  {school} is full but {student} has higher score ({student_score}) than {rejected} ({current[0][1]}).\n")
                status_text.insert(tk.END, f"  {rejected} is rejected and must try another school.\n")
                state["history"][-1]["action"] = "replaced"
                state["history"][-1]["rejected"] = rejected
            else:
                # Student rejected - try next preference
                state["unmatched"].append(student)
                status_text.insert(tk.END, 
                                 f"  {school} is full and {student}'s score ({student_score}) is not high enough.\n")
                state["history"][-1]["action"] = "rejected"
        
        # Update display
        self._draw_animation_state(state, canvas)
        
        # Ensure the latest text is visible
        status_text.see(tk.END)
        
        # Schedule next step if running
        if state["running"]:
            canvas.after(int(state["speed"] * 1000), 
                        lambda: self._animation_run_step(state, canvas, status_text))

    def _draw_animation_state(self, state, canvas):
        """Draw current algorithm state on canvas"""
        # Clear canvas
        canvas.delete("all")
        
        # Get canvas dimensions
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        
        if canvas_width < 50 or canvas_height < 50:
            canvas.after(100, lambda: self._draw_animation_state(state, canvas))
            return
        
        # Draw schools on right
        schools = list(state["schools_dict"].keys())
        school_positions = {}
        school_x = 3 * canvas_width // 4
        
        school_spacing = canvas_height // (len(schools) + 1)
        
        for i, school_name in enumerate(schools):
            y = (i + 1) * school_spacing
            school_positions[school_name] = (school_x, y)
            
            # Get school data
            capacity = state["schools_dict"][school_name]["capacity"]
            accepted = state["schools_dict"][school_name]["accepted"]
            
            # Draw with different color if this is the current school
            fill_color = "#3498db"  # Default blue
            if school_name == state["current_school"]:
                fill_color = "#f39c12"  # Orange for current
            
            # Draw school node
            canvas.create_oval(
                school_x - 25, y - 25, 
                school_x + 25, y + 25, 
                fill=fill_color, outline="black"
            )
            
            # School name
            canvas.create_text(
                school_x, y - 5, 
                text=school_name, 
                font=("Arial", 10, "bold")
            )
            
            # School capacity and current acceptances
            canvas.create_text(
                school_x, y + 15, 
                text=f"Capacity: {capacity} ({len(accepted)} filled)", 
                font=("Arial", 8)
            )
            
            # Draw accepted students list
            if accepted:
                for j, (student, score) in enumerate(accepted):
                    label_y = y + 30 + j * 20
                    # Highlight if this was just accepted
                    text_color = "green" if (state["current_student"] == student and 
                                            state["current_school"] == school_name) else "black"
                    
                    canvas.create_text(
                        school_x, label_y,
                        text=f"{student} ({score})",
                        font=("Arial", 8),
                        fill=text_color
                    )
        
        # Draw unmatched students on left
        students = state["unmatched"]
        student_positions = {}
        student_x = canvas_width // 4
        
        # Title for unmatched
        canvas.create_text(
            student_x, 20,
            text=f"Unmatched Students ({len(students)})",
            font=("Arial", 12, "bold")
        )
        
        student_spacing = min(30, (canvas_height - 50) // max(1, len(students)))
        
        for i, student_name in enumerate(students):
            y = 50 + i * student_spacing
            student_positions[student_name] = (student_x, y)
            
            # Get student data
            score = state["student_dict"][student_name]["score"]
            pref_index = state["pref_index"][student_name]
            prefs = state["student_dict"][student_name]["prefs"]
            
            # Highlight current student
            text_color = "red" if student_name == state["current_student"] else "black"
            
            # Draw student
            canvas.create_text(
                student_x, y,
                text=f"{student_name} (Score: {score})",
                font=("Arial", 9),
                fill=text_color
            )
            
            # Show preferences status
            if pref_index < len(prefs):
                next_pref = prefs[pref_index]
                prefs_str = f"Next: {next_pref}"
            else:
                prefs_str = "No more preferences"
                
            canvas.create_text(
                student_x, y + 15,
                text=prefs_str,
                font=("Arial", 8)
            )
        
        # Draw rejected students if space allows
        rejected_students = set()
        for entry in state["history"]:
            if entry["action"] == "replaced" and entry["rejected"] is not None:
                rejected_students.add(entry["rejected"])
        
        rejected_students = rejected_students - set(students)  # Only those not in unmatched
        
        if rejected_students:
            rejected_x = student_x
            start_y = 50 + len(students) * student_spacing + 40
            
            canvas.create_text(
                rejected_x, start_y - 20,
                text="Rejected Students",
                font=("Arial", 12, "bold")
            )
            
            for i, student_name in enumerate(rejected_students):
                y = start_y + i * 20
                canvas.create_text(
                    rejected_x, y,
                    text=f"{student_name}",
                    font=("Arial", 9),
                    fill="gray"
                )
        
        # Draw legend
        legend_y = 30
        canvas.create_rectangle(10, legend_y - 10, 30, legend_y + 10, fill="#f39c12", outline="black")
        canvas.create_text(90, legend_y, text="Current school", anchor="w", font=("Arial", 8))
        
        canvas.create_text(200, legend_y, text="Red:", fill="red", anchor="w", font=("Arial", 8, "bold"))
        canvas.create_text(230, legend_y, text="Current student", anchor="w", font=("Arial", 8))
        
        canvas.create_text(350, legend_y, text="Green:", fill="green", anchor="w", font=("Arial", 8, "bold"))
        canvas.create_text(390, legend_y, text="Just accepted", anchor="w", font=("Arial", 8))

    #endregion


# Main entry point
if __name__ == "__main__":
    root = tk.Tk()
    app = CollegeAdmissionsApp(root)
    root.mainloop()