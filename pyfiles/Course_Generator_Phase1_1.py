from collections import defaultdict
from datetime import datetime
import io
import nbformat
from nbformat.v4 import new_notebook
from nbformat import validate
from IPython.display import display
from ipywidgets import Layout, Button, widgets, VBox, HBox, Output, Label, Text
import heapq
import json
import difflib

from pyfiles.course_selector import maximize_courses

# Dictionary containing modules and corresponding notebook file paths.
modules = {
    "Unit1": {
    "The Basics of Complex Numbers":"Quantum_Cryptography_Notes/Unit 01 - Quantum Computing and Cryptography/01_ Basics of Complex Numbers/nanomod01-unit01.ipynb",
    "Properties of Complex Numbers":"Quantum_Cryptography_Notes/Unit 01 - Quantum Computing and Cryptography/02_ Properties of Complex Numbers/nanomod02-unit01.ipynb",
    "Complex Numbers on a Plane":"Quantum_Cryptography_Notes/Unit 01 - Quantum Computing and Cryptography/03_ Complex Numbers on a Plane/nanomod03-unit01.ipynb",
    "Complex Vector Spaces":"Quantum_Cryptography_Notes/Unit 01 - Quantum Computing and Cryptography/04_ Complex Vector Spaces/nanomod04-unit01.ipynb",
    "Complex Vector Spaces Linear Combination, Independence, Basis and Dimensions":"Quantum_Cryptography_Notes/Unit 01 - Quantum Computing and Cryptography/05_ Complex Vector Spaces_ Linear Combination, Independence, Basis and Dimensions/nanomod05-unit01.ipynb",
    "Properties and Operations on Vectors and Matrices in Complex Vector Spaces":"Quantum_Cryptography_Notes/Unit 01 - Quantum Computing and Cryptography/06_ Properties and Operations on Vectors and Matrices in Complex Vector Spaces/nanomod06-unit01.ipynb",
    "Advanced Concepts in Complex Vector Spaces":"Quantum_Cryptography_Notes/Unit 01 - Quantum Computing and Cryptography/07_ Advanced Concepts in Complex Vector Spaces/nanomod07-unit01.ipynb",
    "Overview of Tensor Analysis": "Quantum_Cryptography_Notes/Unit 01 - Quantum Computing and Cryptography/08_ Tensor Analysis/nanomod08-unit01.ipynb",
        },
    "Unit2": {
        "From Probabilistic Systems to Quantum Systems" : "Quantum_Cryptography_Notes/Unit 02 - Quantum Computing and Cryptography/09_ Probabilistic to Quantum Systems/nanomod09-unit02.ipynb",
        "Basics of Quantum Computing/Cryptography" : "Quantum_Cryptography_Notes/Unit 02 - Quantum Computing and Cryptography/10_ The Basics/nanomod10-unit02.ipynb",
        "Basics of Measuring a Qubit" :  "Quantum_Cryptography_Notes/Unit 02 - Quantum Computing and Cryptography/11_ Basics of Measuring a Qubit/nanomod11-unit02.ipynb",
        "Visualizing a qubit": "Quantum_Cryptography_Notes/Unit 02 - Quantum Computing and Cryptography/12_ Visualizing a Qubit/nanomod12-unit02.ipynb",
        "General Single-Qubit Measurement": "Quantum_Cryptography_Notes/Unit 02 - Quantum Computing and Cryptography/13_ General Single-Qubit Measurement/nanomod13-unit02.ipynb",
        "Single-Qubit Gates and Operations": "Quantum_Cryptography_Notes/Unit 02 - Quantum Computing and Cryptography/14_ Single-Qubit Gates and Operations/nanomod14-unit02.ipynb",
        "Multi-qubit Systems": "Quantum_Cryptography_Notes/Unit 02 - Quantum Computing and Cryptography/15_ Multi-qubit Systems/nanomod15-unit02.ipynb",
        "Multiple Qubits and Entangled Systems": "Quantum_Cryptography_Notes/Unit 02 - Quantum Computing and Cryptography/16_ Multiple Qubits and Entangled Systems/nanomod16-unit02.ipynb",
        "The EPR Paradox and CHSH Game": "Quantum_Cryptography_Notes/Unit 02 - Quantum Computing and Cryptography/17_ The EPR Paradox and CHSH Game/nanomod17-unit02.ipynb",
        "Multi-Qubit Gates and Operations": "Quantum_Cryptography_Notes/Unit 02 - Quantum Computing and Cryptography/18_ Multi-Qubit Gates and Operations/nanomod18-unit02.ipynb"
        },
    "Unit3": {
        "The Three-Stage Quantum Key Distribution Protocol & Entanglement based QKD": "Quantum_Cryptography_Notes/Unit 03 - Quantum Computing and Cryptography/22_ The Three-Stage Quantum Key Distribution Protocol/nanomod22-unit03.ipynb"
    }
}

# Dictionary mapping concepts to their corresponding final quiz notebook paths.
final_quiz = {
    "The Basics of Complex Numbers":"Quantum_Cryptography_Notes/Unit 01 - Quantum Computing and Cryptography/01_ Basics of Complex Numbers/finalquiz01.ipynb",
    "Properties of Complex Numbers":"Quantum_Cryptography_Notes/Unit 01 - Quantum Computing and Cryptography/02_ Properties of Complex Numbers/finalquiz02.ipynb",
    "Complex Numbers on a Plane":"Quantum_Cryptography_Notes/Unit 01 - Quantum Computing and Cryptography/03_ Complex Numbers on a Plane/finalquiz03.ipynb",
    "Complex Vector Spaces":"Quantum_Cryptography_Notes/Unit 01 - Quantum Computing and Cryptography/04_ Complex Vector Spaces/finalquiz04.ipynb",
    "Complex Vector Spaces Linear Combination, Independence, Basis and Dimensions":"Quantum_Cryptography_Notes/Unit 01 - Quantum Computing and Cryptography/05_ Complex Vector Spaces_ Linear Combination, Independence, Basis and Dimensions/finalquiz05.ipynb",
    "Properties and Operations on Vectors and Matrices in Complex Vector Spaces":"Quantum_Cryptography_Notes/Unit 01 - Quantum Computing and Cryptography/06_ Properties and Operations on Vectors and Matrices in Complex Vector Spaces/finalquiz06.ipynb",
    "Advanced Concepts in Complex Vector Spaces":"Quantum_Cryptography_Notes/Unit 01 - Quantum Computing and Cryptography/07_ Advanced Concepts in Complex Vector Spaces/finalquiz07.ipynb",
    "Overview of Tensor Analysis": "Quantum_Cryptography_Notes/Unit 01 - Quantum Computing and Cryptography/08_ Tensor Analysis/finalquiz08.ipynb",
    "From Probabilistic Systems to Quantum Systems" : "Quantum_Cryptography_Notes/Unit 02 - Quantum Computing and Cryptography/09_ Probabilistic to Quantum Systems/finalquiz09.ipynb",
    "Basics of Quantum Computing/Cryptography" : "Quantum_Cryptography_Notes/Unit 02 - Quantum Computing and Cryptography/10_ The Basics/finalquiz10.ipynb",
    "Basics of Measuring a Qubit": "Quantum_Cryptography_Notes/Unit 02 - Quantum Computing and Cryptography/11_ Basics of Measuring a Qubit/finalquiz11.ipynb",
    "Visualizing a qubit": "Quantum_Cryptography_Notes/Unit 02 - Quantum Computing and Cryptography/12_ Visualizing a Qubit/finalquiz12.ipynb",
    "General Single-Qubit Measurement": "Quantum_Cryptography_Notes/Unit 02 - Quantum Computing and Cryptography/13_ General Single-Qubit Measurement/finalquiz13.ipynb",
    "Single-Qubit Gates and Operations": "Quantum_Cryptography_Notes/Unit 02 - Quantum Computing and Cryptography/14_ Single-Qubit Gates and Operations/finalquiz14.ipynb",
    "Multi-qubit Systems": "Quantum_Cryptography_Notes/Unit 02 - Quantum Computing and Cryptography/15_ Multi-qubit Systems/finalquiz15.ipynb",
    "Multiple Qubits and Entangled Systems": "Quantum_Cryptography_Notes/Unit 02 - Quantum Computing and Cryptography/16_ Multiple Qubits and Entangled Systems/finalquiz16.ipynb",
    "The EPR Paradox and CHSH Game": "Quantum_Cryptography_Notes/Unit 02 - Quantum Computing and Cryptography/17_ The EPR Paradox and CHSH Game/finalquiz17.ipynb",
    "Multi-Qubit Gates and Operations": "Quantum_Cryptography_Notes/Unit 02 - Quantum Computing and Cryptography/18_ Multi-Qubit Gates and Operations/finalquiz18.ipynb"
}

# A list of specific cells to exclude during notebook generation.
excluded_cells = ["learningoutcomes", "warmup", "summary", "finalquiz", "conclusions"]

class NotebookGenerator:
    _debug_log_enabled = True

    def __init__(self, modules):
        self.debug_log(f"\n\nGenerator started at {datetime.now()}")
        # Initialize the notebook generator with the provided modules
        self.modules = modules
        self.outcome_concepts_mapping = defaultdict(list)
        self.selected_concepts = set()  # Track selected concepts
        self.notebook_cells = {}  # Store cells for each notebook
        self.notebook_metadata = {}  # Store metadata for each notebook
        self.accordion = self.create_accordion()  # Create the accordion UI for module selection
        self.output = Output()  # Output widget for status updates
        self.output2 = Output()  # Output widget for additional information
        self.submit_button = Button(description='Submit', disabled=False)  # Submit button for generating the notebook
        self.clear_selection_button = Button(description='Clear Selection', disabled=False)  # Button to clear selected concepts
        self.pre_req_concepts = []  # Track pre-requisite concepts selected
        self.setup_ui()  # Set up the UI components

    def debug_log(self, log: str):
        if not self._debug_log_enabled:
            return
        
        with open('debug.log', 'a') as log_file:
            log_file.write(log + '\n')

    # Appends user interactions or actions to a JSON file for tracking or analytics
    def append_action(self, new_data):
        file_path = 'actions.json'
        try:
            with open(file_path, 'r') as json_file:
                existing_data = json.load(json_file)
        except FileNotFoundError:
            existing_data = []

        # Append new action to the log
        if isinstance(existing_data, list):
            existing_data.append(new_data)
        else:
            existing_data = [existing_data, new_data]
        with open(file_path, 'w') as json_file:
            json.dump(existing_data, json_file, indent=4)

    # Accordion UI for selecting learning outcomes (creates a UI for each module)
    def create_accordion(self):
        accordion_parent = []
        accordion_children = []
        for unit_name in self.modules.keys():
            accordion_children = []
            for module_name in self.modules[unit_name].keys():
                select_multiple = widgets.SelectMultiple(
                    options=self.get_outcomes_for_module(module_name, unit_name),
                    value=[],
                    description='Outcomes',
                    disabled=False,
                    layout=Layout(width='960px', height='175px')
                )
                accordion_children.append(select_multiple)
            accordion_parent.append(widgets.Accordion(children=accordion_children, layout=Layout(width='1000px')))
        for j, unit_name in enumerate(self.modules.keys()):
            for i, module_name in enumerate(self.modules[unit_name].keys()):
                accordion_parent[j].set_title(i, module_name)
        return accordion_parent

    # Extracts the learning outcomes for a given module
    def get_outcomes_for_module(self, module_name, unit_name):
        with io.open(modules[unit_name][module_name], 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, 4)
            self.notebook_cells[module_name] = nb.cells  # Store notebook cells
            self.notebook_metadata[module_name] = nb.metadata.module_details  # Store notebook metadata
            return nb.metadata.module_details.module_outcomes  # Return learning outcomes

    # Handle the user's selection change, update the selected concepts and include quizzes if needed
    def on_change(self, change):
        with self.output:
            if change['type'] == 'change' and change['name'] == 'value':
                selected_outcome = change['new'][-1]
                self.append_action({'id': self.student_id.value, 'type': 'outcome-click', 'value': selected_outcome})
                for i, notebook_metadata in enumerate(self.notebook_metadata.values()):
                    module_outcomes = notebook_metadata.module_outcomes
                    if selected_outcome in module_outcomes:
                        module_index = module_outcomes.index(selected_outcome)
                        cell_concepts = notebook_metadata.module_outcomes_mapping[module_index]
                        self.debug_log(f'Selected a concept with module outcome {selected_outcome}. Cell concepts {cell_concepts}')
                        for cell in cell_concepts:
                            if "final-quiz" in cell:  # If a final quiz exists for this concept
                                module_final_quiz = list(final_quiz.values())[i]  # Get the corresponding final quiz
                                notebook = new_notebook()
                                with io.open(module_final_quiz, 'r', encoding='utf-8') as f:
                                    nb = nbformat.read(f, 4)
                                validate(nb)
                                for quiz_cell in nb.cells:
                                    notebook.cells.append(quiz_cell)
                                with open(f'Modules/{cell}.ipynb', 'w', encoding='utf-8') as f:
                                    nbformat.write(notebook, f)
                            elif cell not in self.selected_concepts:
                                self.outcome_concepts_mapping[selected_outcome].append(cell)
                                self.debug_log(f'Added {cell} to selected concepts. New set {self.selected_concepts}')
                                self.selected_concepts.add(cell)  # Add the concept if not already selected

    # Retrieve the notebook cells based on the cell ID
    def get_notebook_cells_from_cell_id(self, cell_id):
         return next(
            cell
            for notebook_cell in self.notebook_cells.values()
            for cell in notebook_cell
            if cell.metadata.cell_details.cell_ID == cell_id
        )
 
    def on_submit_clicked_v2(self, b):
        """
        Handles the submission when the user clicks the "Submit" button.
        This version uses precedence-based knapsack to ensure that if a course cannot be included
        due to time constraints, neither the course nor its prerequisite chain will be included.

        Args:
            b: The button click event (from the UI)
        """
        with self.output2:
            total_time = (self.estimated_time.value and int(self.estimated_time.value)) or 10000
            self.debug_log(f"\n\nUser selected following concepts. {self.selected_concepts}")
            course_keys = set(self.selected_concepts.copy())  # Work on a copy to prevent modifying the original
            courses = {}

            # Create a list copy of course_keys to avoid modifying the set during iteration
            pending_courses = list(course_keys)

            # Iterate through each selected concept and convert it into the desired format
            while pending_courses:
                concept = pending_courses.pop(0)  # Remove and process the first item

                if concept in courses:
                    continue  # Skip if already processed
                
                # Get the cell data for the concept
                concept_cell = self.get_notebook_cells_from_cell_id(concept)

                # Create a dictionary for the course
                course_dict = {
                    'id': concept,
                    'estimated_time': int(concept_cell.metadata.cell_details.cell_estimated_time),
                    'prerequisites': []
                }

                # Add its prerequisites to the dictionary
                for pre_req in concept_cell.metadata.cell_details.cell_prereqs:
                    course_dict['prerequisites'].append(pre_req)

                    # If the prerequisite has not been processed yet, add it to pending courses
                    if pre_req not in courses:
                        pending_courses.append(pre_req)

                # Add the course dictionary to the final courses dictionary
                courses[concept] = course_dict


            pre_req_concepts_set = set(self.pre_req_concepts)
            pre_req_known_cell_ids = set()

            for module in self.notebook_cells.values():
                for cell in module:
                    if len(set(cell.metadata.cell_details.cell_concepts) & pre_req_concepts_set):
                        pre_req_known_cell_ids.add(cell.metadata.cell_details.cell_ID)

            selected_courses, count = maximize_courses(list(courses.values()), total_time, list(self.selected_concepts), pre_req_known_cell_ids, self.debug_log)
            self.debug_log(f"Filtered Courses {selected_courses}\n")
            notebook = new_notebook()
            for course in selected_courses:
                concept_cell = self.get_notebook_cells_from_cell_id(course)
                concept = concept_cell.metadata.cell_details.cell_ID
                notebook.cells.append(concept_cell)

            # Save the generated notebook to the "Modules" directory
            with open(f'Modules/Courses2.ipynb', 'w', encoding='utf-8') as f:
                nbformat.write(notebook, f)

            self.append_action({'id': self.student_id.value, 'type': 'submit-click', 'value': selected_courses})

            # Provide feedback to the user
            print("Notebook created successfully. Please navigate to the Modules folder and find the Course file to check out the Notebook created.")
            if self.estimated_time.value:
                print("Few concepts may be intentionally ignored due to the time constraint. To learn the full course, consider spending more time.")


    def on_submit_clicked(self, b):
        """
        Handles the user's submission when they click the "Submit" button.
        This function calculates the total profit (importance) of the selected concepts and their prerequisites,
        and generates a notebook that includes the most important concepts, while respecting the time constraint set by the user.

        The function works as follows:
        1. Calculates the importance (profit) of each selected concept using DFS, factoring in prerequisites.
        2. Selects the most important concepts based on available time, using DFS to ensure dependencies are respected.
        3. Generates a notebook that contains the selected cells (concepts) and saves it to a file.

        Args:
            b: The button click event (from the UI)
        """

        # Output any messages to the output widget
        with self.output2:
            # Initialize a new Jupyter notebook object
            notebook = new_notebook()

            # Variables to store the selected notebook cells and their IDs
            selected_notebook_cells = []
            selected_notebook_ids = []
            
            # Order is used to keep track of the order in which cells are processed
            order = 1
            
            # Sets to track visited and selected cells (to prevent duplicates)
            seen = set()
            visited = set()

            # Get the total available time the user has entered (default to 10,000 minutes if not provided)
            total_time = (self.estimated_time.value and int(self.estimated_time.value)) or 10000

            def dfsWeightCalc(cellId, curr_profit, order):
                """
                Recursively calculates the total importance (profit) of a concept (cell) and its dependencies (prerequisites).
                
                The importance of a course or concept is determined by:
                - Its estimated time to complete: The lower the time, the higher its relative profit.
                - The importance (profit) of its prerequisite concepts.
                
                Key Idea:
                - High-importance concepts are those that provide high value (profit) relative to the time required to complete them.
                - Low-importance concepts are those that take up a lot of time but provide little relative value.
                
                How Profit is Calculated:
                - Each concept (or learning outcome) starts with an initial `profit` of 1 (this can be customized).
                - The profit is divided by the time required to complete the concept (`1 / estimated_time`).
                - A concept with important prerequisites will have their profits added to its own profit, making it more valuable.

                High-importance concepts:
                - Concepts that are fundamental, have important prerequisites, or require less time to complete.
                - Example: A basic introduction to quantum computing might be fundamental for more advanced topics.

                Low-importance concepts:
                - Concepts that take a long time but don't provide as much value in terms of learning outcomes.
                - Example: Advanced but niche topics that require a lot of time but may not be foundational for other concepts.
                
                Args:
                    cellId (str): The ID of the current concept (cell) being processed.
                    curr_profit (float): The current importance/profit of the concept (initially set to 1).
                    order (int): The order in which concepts are processed (used for sequencing concepts).

                Returns:
                    float: The total fractional profit of the concept and its dependencies (prerequisites).
                """

                totlfracProfit = 0  # Initialize total profit for the current concept

                # Retrieve prerequisite concepts for the current concept (cell)
                neighbours = self.get_notebook_cells_from_cell_id(cellId).metadata.cell_details.cell_prereqs

                # Recursively process each prerequisite
                for neighbour in neighbours:
                    fracProfit = 0  # Fractional profit for the prerequisite
                    neighbour_cell = self.get_notebook_cells_from_cell_id(neighbour)
                    if neighbour not in visited:  # Only process unvisited prerequisites
                        visited.add(neighbour)
                        print("A pre req found ->", neighbour_cell.metadata.cell_details.cell_ID)

                        
                        # Recursively calculate the profit of the prerequisite and its dependencies
                        next_profit = curr_profit
                        fracProfit += next_profit / int(neighbour_cell.metadata.cell_details.cell_estimated_time) + dfsWeightCalc(neighbour, next_profit, order)

                        # Assign the current order and profit to the prerequisite cell
                        neighbour_cell.order = order
                        order += 1
                        neighbour_cell.profit = next_profit
                        neighbour_cell.fracProfit = fracProfit

                        # Add the profit of the prerequisite to the total profit
                        totlfracProfit += fracProfit
                    elif neighbour in visited:
                        # If the prerequisite was already visited, add its stored profit
                        totlfracProfit += neighbour_cell.fracProfit

                return totlfracProfit

            print('selected concepts', self.selected_concepts)
            for concept in self.selected_concepts:
                concept_cell = self.get_notebook_cells_from_cell_id(concept)

                # Only process unvisited concepts
                if concept not in visited:
                    visited.add(concept)
                    
                    curr_profit = 1  # Each concept starts with a base profit of 1
                    print("Process Concept", concept)
                    # Calculate the total profit (importance) of the concept and its prerequisites
                    fracProfit = dfsWeightCalc(concept, curr_profit, order)

                    # Assign the order and profit to the current concept
                    concept_cell.order = order
                    order += 1
                    concept_cell.profit = curr_profit
                    concept_cell.fracProfit = fracProfit + curr_profit / int(concept_cell.metadata.cell_details.cell_estimated_time)

            def dfs(cellId, total_time):
                """
                Selects the best concepts to include in the notebook based on available time.
                This function uses DFS to explore each concept's prerequisites and ensures that only those that fit
                within the time limit are included.

                Args:
                    cellId (str): The ID of the current concept (cell) being processed.
                    total_time (int): The remaining time available to include concepts.

                Returns:
                    int: The updated remaining time after including the concept and its prerequisites.
                """

                # Get the prerequisites (dependencies) for the current concept
                neighbours = self.get_notebook_cells_from_cell_id(cellId).metadata.cell_details.cell_prereqs
                neighbour_cells = []

                # Retrieve the notebook cells for each prerequisite
                for neighbour in neighbours:
                    neighbour_cells.append(self.get_notebook_cells_from_cell_id(neighbour))

                # Sort the prerequisite cells based on their calculated fractional profit
                neighbour_cells = sorted(neighbour_cells, reverse=True, key=lambda x: x.fracProfit)

                # Process each prerequisite and include it if it fits within the available time
                for neighbour_cell in neighbour_cells:
                    neighbour = neighbour_cell.metadata.cell_details.cell_ID

                    if total_time > 0 and neighbour not in seen and neighbour_cell.metadata.cell_details.cell_concepts[0] not in self.pre_req_concepts:
                        seen.add(neighbour)  # Mark the prerequisite as selected
                        
                        # Recursively process the prerequisites of the neighbour
                        total_time = dfs(neighbour, total_time)
                        
                        # Get the time required for the neighbour concept
                        cell_time = int(neighbour_cell.metadata.cell_details.cell_estimated_time)

                        # If the concept fits within the available time, add it to the notebook
                        if cell_time <= total_time:
                            total_time -= cell_time
                            selected_notebook_cells.append(neighbour_cell)
                            selected_notebook_ids.append(neighbour)
                        else:
                            print(f"******* Cell won't fit cell - {neighbour}. Pending Time {total_time}, Cell time {cell_time}")
                    elif total_time <= 0:
                        print(f"******* Time might not available for cell - {neighbour}. Pending time {total_time}")

                return total_time

            # Iterate through the selected concepts and process them using DFS
            concept_cells = []
            for concept in self.selected_concepts:
                concept_cells.append(self.get_notebook_cells_from_cell_id(concept))

            # Sort the selected concepts by their calculated fractional profit
            concept_cells = sorted(concept_cells, reverse=True, key=lambda x: x.fracProfit)

            # Include concepts and their prerequisites based on the available time
            for concept_cell in concept_cells:
                concept = concept_cell.metadata.cell_details.cell_ID
                if total_time > 0 and concept not in seen and concept_cell.metadata.cell_details.cell_concepts[0] not in self.pre_req_concepts:
                    seen.add(concept)
                    total_time = dfs(concept, total_time)
                    cell_time = int(concept_cell.metadata.cell_details.cell_estimated_time)
                    if cell_time <= total_time:
                        total_time -= cell_time
                        selected_notebook_cells.append(concept_cell)
                        selected_notebook_ids.append(concept)

            # Sort the selected notebook cells by their calculated profit and add them to the notebook
            selected_notebook_cells = sorted(selected_notebook_cells, key=lambda x: x.fracProfit)
            print("Un-Ordered", selected_notebook_ids)
            print("COUNT", len(selected_notebook_cells))
            print("SELECTED NOTEBOOK CELLS", list(map(lambda x:x.metadata.cell_details.cell_ID, selected_notebook_cells)))
            for item in selected_notebook_cells:
                notebook.cells.append(item)

            # Save the generated notebook to the "Modules" directory
            with open(f'Modules/Course.ipynb', 'w', encoding='utf-8') as f:
                nbformat.write(notebook, f)

            # Log the submission action
            self.append_action({'id': self.student_id.value, 'type': 'submit-click', 'value': selected_notebook_ids})

            # Provide feedback to the user
            print("Notebook created successfully. Please navigate to the Modules folder and find the Course file to check out the Notebook created.")
            if self.estimated_time.value:
                print("Few concepts may be intentionally ignored due to the time constraint. To learn the full course, consider spending more time.")


    # Handles clearing user selections
    def clear_selection_clicked(self, b):
        self.append_action({'id': self.student_id.value, 'type': 'clear-selection-click', 'value': 'Selection cleared'})
        with self.output:
            self.output.clear_output()
            self.selected_concepts.clear()
        with self.output2:
            self.output2.clear_output()
            print("Selection cleared")
                
    def handle_query(self, b):
        with self.output2:
            self.output2.clear_output()
            prompt = self.prompt_input.value
            if prompt:
                response = self.query_openai(prompt)
                print(response)
            else:
                print("Please enter a prompt.")

    def multi_checkbox_widget(self, descriptions):
        """ Widget with a search field and lots of checkboxes """
        search_widget = widgets.Text()
        options_dict = {description: widgets.Checkbox(description=description, value=False) for description in descriptions}
        options = [options_dict[description] for description in descriptions]
        #options_widget = widgets.VBox(options)
        widge = []
        for i in range(0, len(options), 3):
            row = options[i:i+3]
            widge.append(widgets.HBox(row, layout={'width': '1000px'}))
        options_widget = widgets.VBox(widge)       
        multi_select = widgets.VBox([search_widget, options_widget])
        
        def on_check_select_change(change):
            if change['type'] == 'change' and change['name'] == 'value' and change['new'] == True:
                self.pre_req_concepts.append(change['owner'].description)
                self.append_action({
                    'id': self.student_id.value,
                    'type': 'check-box-click',
                    'value': change['owner'].description,
                })
                # print(self.pre_req_concepts)

        for option in options:
            option.observe(on_check_select_change)

        # Wire the search field to the checkboxes
        def on_text_change(change):
            search_input = change['new']
            if search_input == '':  
                # Reset search field
                new_options = [options_dict[description] for description in descriptions]
            else:
                # Filter by search field using difflib.
                close_matches = difflib.get_close_matches(search_input, descriptions, cutoff=0.0)
                new_options = [options_dict[description] for description in close_matches]
            #options_widget. = new_options
            widge = []
            for i in range(0, len(new_options), 3):
                row = new_options[i:i+3]
                widge.append(widgets.HBox(row, layout={'width': '1000px'}))
            options_widget.children = widge

        search_widget.observe(on_text_change, names='value')
        return multi_select
        
    def grade_firstquiz(self, n):
        with io.open(list(final_quiz.values())[0], 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, 4)
        prompt = ''
        questionflip = True
        prompts = []
        for quiz_cell in nb.cells[1:]:
            if questionflip:
                prompts.append('Question: '+ quiz_cell.source)
            else:
                prompts.append('Answer: '+ quiz_cell.source)
            questionflip = not questionflip
        print(prompts)
        with self.output2:
            self.output2.clear_output()
            if prompts:
                response = self.query_openai(prompts)
                print(response)
            else:
                print("Please enter a prompt.")

    # Set up the UI components for displaying
    def setup_ui(self):
        for accordion in self.accordion:
            for selectedMultiple in accordion.children:
                selectedMultiple.observe(self.on_change)

        self.clear_selection_button.on_click(self.clear_selection_clicked)
        self.submit_button.on_click(self.on_submit_clicked_v2)

        self.estimated_time = Text(placeholder='Estimated Time', disabled=False, layout=Layout(width='500px'))
        self.estimated_time_label = Label(value='Estimated Time (in mins): ')

        self.select_mode = widgets.RadioButtons(
            options=['Concept - Driven Learning Mode', 'Quiz - Driven Learning Mode'],
            description='Select Mode: '
        )

        # self.quizzes = widgets.SelectMultiple(
        #         options=self.notebook_metadata.keys(),
        #         value=[],
        #         disabled=False,
        #         layout=Layout(width='1000px', height='175px')
        #     )
        self.notebooks_concepts = [
          x for concepts in self.notebook_metadata.values()
          for x in concepts.module_concepts 
        ]

        self.student_id_label = Label(value='Enter your student ID: ')
        self.student_id = Text(placeholder='Enter your Student ID', layout=Layout(width='400px'))

        self.pre_reqs_label = Label(value='Let us know if already know below topics: ')
        self.pre_reqs = self.multi_checkbox_widget(self.notebooks_concepts)
        self.prompt_input = Text(placeholder='Enter your prompt here', layout=Layout(width='400px'))
        self.query_button = Button(description='Ask OpenAI', disabled=False)
        self.query_button.on_click(self.handle_query)

        self.grade_button = Button(description='Grade', disabled=False)
        self.grade_button.on_click(self.grade_firstquiz)
        
        self.heading_label = widgets.HTML(value='<b>Select the Outcomes from below Chapters to generate Notebooks</b>')
        # self.heading_label.layout = widgets.Layout(font_weight='bold')
        
        # Display all components as a VBox layout
        display(VBox([
            #HBox([self.select_mode]),
            HBox([self.student_id_label]),
            HBox([self.student_id]),
            HBox([self.pre_reqs_label]),
            HBox([self.pre_reqs]),
            HBox([self.heading_label]),
            HBox([Label(value='Unit 01 - Linear Algebra')]),
            HBox([self.accordion[0]]),
            HBox([Label(value='Unit 02 - Quantum Computing')]),
            HBox([self.accordion[1]]),
            HBox([Label(value='Unit 03 - Quantum Networking Protocols')]),
            HBox([self.accordion[2]]),
            # HBox([self.quizzes]),
            HBox([self.estimated_time_label, self.estimated_time]),
            HBox([self.submit_button, self.clear_selection_button]),
            # HBox([self.prompt_input, self.query_button]),
            # HBox([self.grade_button]),
            HBox([self.output2]),
        ]))

# Initialize the notebook generator with modules
NotebookGenerator(modules)
