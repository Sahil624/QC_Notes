import asyncio
from datetime import datetime, timedelta
from functools import wraps
import json
from tkinter import *
from operator import add
import os
import math
import time
from Quantum_Node import Node
from Quantum_Edge import Edge
from Drag_and_drop_manager import DragManager
# from Home import Home as Hom
from global_variables import *
from E91Util import *
# from PIL import Image,ImageTk
from Utils import start, setGlobalValues, periodic_update
from dto.dto import insert, select, fetchallRows
from Quantum_Circuits import *
import ipywidgets as widgets
from ipycanvas import Canvas as PyCanvas, MultiCanvas, hold_canvas

from IPython.display import display

import time

def debounce(wait_time_ms):
    """
    Decorator that ensures a function is called at most once every wait_time_ms milliseconds.
    
    Args:
        wait_time_ms (int): Minimum time between function calls in milliseconds
    """
    def decorator(fn):
        last_called = None
        
        @wraps(fn)
        def debounced(*args, **kwargs):
            nonlocal last_called
            current_time = datetime.now()
            
            # If this is the first call or enough time has passed since last call
            if last_called is None or \
               (current_time - last_called) > timedelta(milliseconds=wait_time_ms):
                last_called = current_time
                return fn(*args, **kwargs)
            
        return debounced
    return decorator

def toggle_button(button: widgets.Button):
    if button.layout.visibility == 'hidden':
        button.layout.visibility = 'visible'
    else:
        button.layout.visibility = 'hidden'

class MockEvent:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Quantum_Network():
    canvas:PyCanvas=None

    def __init__(self, selectedMode, selectedProtocol, message_var, ksu_id_var, grid_size):
        global number_of_dots
        # self.window = Tk()
        self.window = widgets.VBox() # For vertical layout
        # self.window.title('Quantum Key Distribution Network') 
        self.canvas_size = size_of_board
        # screen_width = self.window.winfo_screenwidth()
        # screen_height = self.window.winfo_screenheight()
        # self.mode = homeSelf['selectedMode']
        # self.protocol = homeSelf['selectedProtocol']
        # self.message = homeSelf['message_var']
        # self.ksu_id_var = homeSelf['ksu_id_var']
        # self.selectedtask = homeSelf['selectedtask']
        self.mode = selectedMode
        self.protocol = selectedProtocol
        self.message = message_var
        self.ksu_id_var = ksu_id_var
        self.selectedtask = widgets.Text()
        self.selectedtask.value = send_message
        number_of_dots=grid_size
        # self.selectedtask.set(send_message)
        # self.window.state('zoomed')
        # self.window.attributes("-fullscreen", True)
        self.continue_btn = widgets.Button()
        self.continue_btn.layout.display = 'none'
        self.start_transition_btn = widgets.Button(description='Generate key')
        self.start_transition_btn.on_click(self.callTransitionButtonClick)

        message_label = widgets.Label(value = 'Enter a message to communicate:')
        self.message_entry = widgets.Text()
        send_message_button = widgets.Button(description = 'Send Message')
        send_message_button.on_click(self.send_message_classical)

        self.message_input = widgets.HBox([message_label, self.message_entry, send_message_button])
        self.node_selection_counter = 0
        self.key_generated = False
        self.first_node_selected = 0

        self.bloch_output = widgets.Output()
        with self.bloch_output:
            print("Sphere Output")
        self.message_output = widgets.Output()
        self.adjacency_matrix =  [[0 for col in range(number_of_dots*number_of_dots)] for row in range(number_of_dots*number_of_dots)]
        # print(screen_width, screen_height, self.canvas_size)
        # Create Frames
        # self.grid_frame = Frame(
        #     self.window, 
        #     width=screen_width*.20, 
        #     height=self.canvas_size
        # )
        
        # self.grid_frame.grid(row=0, column=0, padx=10, pady=10)

        self.grid_frame = widgets.HBox() # For horizontal layout

        # self.display_frame = Frame(self.window, width= screen_width*.5, height=self.canvas_size+100)
        # self.display_frame.grid(row=0, column=4, padx=10, pady=10)
        self.display_frame =  widgets.Output()

        # self.controls_frame = Frame(self.window, width=screen_width*.2, height=200)
        # self.controls_frame.grid(row=1, column=0, padx=10, pady=10, sticky='W')

        # self.canvas = Canvas(self.grid_frame, width=self.canvas_size, height=self.canvas_size)
        # self.canvas = PyCanvas(width=self.canvas_size, height=self.canvas_size)

        self.multi_canvas = MultiCanvas(3, width=self.canvas_size, height=self.canvas_size)
        self.bg_canvas = self.multi_canvas[0]
        self.ball_canvas = self.multi_canvas[1]
        self.canvas = self.multi_canvas[2]

        self.canvas.on_client_ready(self.draw)

        # self.left_controls_frame = Frame(self.controls_frame)
        # self.left_controls_frame.grid(column=0, row=0, sticky="NW")

        # self.right_controls_frame = Frame(self.controls_frame)
        # self.right_controls_frame.grid(column=1, row=0, sticky="NE")
        # self.setup_board_ipy()
        # self.grid_size_var=IntVar()
        # self.grid_size_var.set(5)

        self.grid_size_var=widgets.IntText(grid_size)

        self.qc = intialize_circuit(self.window)
        
        
        self.switch_btn_text = 'Switch to arrangement mode'
        
        '''self.switch_btn_text = 'Switch to arrangement mode'
        self.switch_mode_btn = Button(left_controls_frame,text = self.switch_btn_text, command = self.switch_mode)'''

        # name_label = Label(self.left_controls_frame, text = 'Enter the grid size:')
        name_label = widgets.Label(value='Enter the grid size:')
        # name_entry = Entry(self.left_controls_frame,textvariable = self.grid_size_var)
        name_entry = widgets.IntText(
            value=5,
            description='Grid size:',
            disabled=False
        )
        # sub_btn=Button(self.left_controls_frame,text = 'Submit', command = self.submit)
        sub_btn = widgets.Button(description="Submit")
        sub_btn.on_click(self.submit)

        # reset_btn = Button(self.right_controls_frame,text = 'Reset', command = self.reset)
        reset_btn = widgets.Button(
            description='Reset',
            button_style='primary'  # or 'success', 'info', 'warning', 'danger'
        )
        reset_btn.on_click(self.reset)
        #home_btn = Button(self.right_controls_frame, text='Reset Selection', command=self.onHome)

        # name_label.grid(row=0,column=0, padx=5, sticky='W')
        # name_entry.grid(row=0,column=1, padx=5, sticky='W')
        # sub_btn.grid(row=0,column=2, padx= 5, sticky='W')

        # reset_btn.grid(row=0, column=0, padx=5, sticky='E')
        #home_btn.grid(row=0,column=1, padx=5, sticky='E')
        # console_label = Label(self.right_controls_frame, text = 'Check console for logs')
        # console_label.grid(row=5, column=0, padx=5, sticky='W')
        #self.switch_mode_btn.grid(row=1, column=0, padx=5,sticky='W')
        self.updateControls()

        '''ksu_id_label = Label(left_controls_frame, text = 'Give the KSU ID:')
        ksu_id_entry = Entry(left_controls_frame,textvariable = self.ksu_id_var)

        ksu_id_label.grid(row=2, column=0, padx=5, sticky='E')
        ksu_id_entry.grid(row=2, column=1, padx=5, sticky='E')'''


        # Organize controls
        self.controls = widgets.VBox([
            widgets.HBox([self.grid_size_var, sub_btn, reset_btn]),
            widgets.HBox([self.continue_btn, self.start_transition_btn])
        ])
        # self.window.mainloop()
        self.dragging = False
        self.drag_node = None
        self.canvas.on_mouse_down(self.handle_mouse_down)
        self.canvas.on_mouse_move(self.handle_mouse_move)
        self.canvas.on_mouse_up(self.handle_mouse_up)

    def draw(self):
        self.setup_board_ipy()
        toggle_button(self.message_input)
        toggle_button(self.start_transition_btn)

        # self.canvas.pack(fill = "both", expand = False)
        # path = os.path.dirname(__file__)
        # my_file = path+'/map2.jpeg'
        # img= ImageTk.PhotoImage(Image.open(my_file))    
        # self.canvas.create_image( 0, 0, image = img, anchor = "nw")

        # Load and scale background image
        # path = os.path.dirname(__file__)
        # my_file = path+'/map2.jpeg'
        # original_img = Image.open(my_file)
        # resized_img = original_img.resize((int(self.canvas_size), int(self.canvas_size)), Image.Resampling.LANCZOS)
        # self.bg_image = ImageTk.PhotoImage(resized_img)
        # self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")


        """Load and display background map"""

        path = os.path.dirname(__file__)
        my_file = path+'/map2.jpeg'
        bg = widgets.Image.from_file(my_file)
        # bg = widgets.Image.from_url('https://elfsight.com/wp-content/uploads/2020/03/google-maps-examples1.jpg')
        with hold_canvas(self.bg_canvas):
            self.bg_canvas.draw_image(bg, 50, 50)

    def handle_mouse_down(self, x, y):
        """Handle mouse down event"""
        if self.mode == rearrange:
            for node in self.node_list:
                node_x, node_y = node.position
                if math.sqrt((x - node_x)**2 + (y - node_y)**2) <= dot_width:
                    self.dragging = True
                    self.drag_node = node
                    break
        else:
            # Handle transmission mode clicks
            clicked_node = self.find_clicked_node(x, y)
            if clicked_node:
                self.node_click(MockEvent(x, y))

    @debounce(wait_time_ms=100)
    def handle_mouse_move(self, x, y):
        """Handle mouse move event"""
        if self.mode == rearrange and self.dragging and self.drag_node:
            # Update node position
            self.drag_node.position = [x, y]
            
            # Redraw everything in one go
            with hold_canvas(self.canvas):
                # Clear canvas
                self.canvas.clear()
                
                # Draw grid lines
                self._draw_grid()
                
                # Draw all edges with updated positions
                for edge in self.stroked_edge_list:
                    # Find the other node in the edge
                    other_node = None
                    if edge.nodes[0] == self.drag_node.id:
                        other_node = next(n for n in self.node_list if n.id == edge.nodes[1])
                        # Update edge start position
                        edge.position = [x, y, other_node.position[0], other_node.position[1]]
                    elif edge.nodes[1] == self.drag_node.id:
                        other_node = next(n for n in self.node_list if n.id == edge.nodes[0])
                        # Update edge end position
                        edge.position = [other_node.position[0], other_node.position[1], x, y]
                    
                    self._draw_edge(edge)
                
                # Draw all nodes on top
                for node in self.node_list:
                    self._draw_node(node)

    def handle_mouse_up(self, x, y):
        """Handle mouse up event"""
        self.dragging = False
        self.drag_node = None

    def _draw_grid(self):
        """Draw the grid lines"""
        self.canvas.set_line_dash([5, 5])
        self.canvas.stroke_style = 'black'
        self.canvas.line_width = 2
        
        for i in range(number_of_dots):
            for j in range(number_of_dots):
                start_x = i * distance_between_dots + distance_between_dots/2
                end_x = j * distance_between_dots + distance_between_dots/2
                
                if j != number_of_dots-1:
                    self.canvas.stroke_line(
                        start_x, end_x,
                        start_x, end_x + distance_between_dots
                    )
                if i != number_of_dots-1:
                    self.canvas.stroke_line(
                        start_x, end_x,
                        start_x + distance_between_dots, end_x
                    )
        self.canvas.set_line_dash([])

    def _draw_node(self, node):
        """Draw a single node"""
        self.canvas.fill_style = node.color
        self.canvas.stroke_style = node.color
        self.canvas.begin_path()
        self.canvas.arc(node.position[0], node.position[1], dot_width/2, 0, 2 * math.pi)
        self.canvas.fill()
        self.canvas.stroke()

    def _draw_edge(self, edge):
        """Draw a single edge"""
        # Draw main line
        self.canvas.stroke_style = edge_color
        self.canvas.line_width = edge_width
        self.canvas.set_line_dash([])
        
        self.canvas.begin_path()
        self.canvas.move_to(edge.position[0], edge.position[1])
        self.canvas.line_to(edge.position[2], edge.position[3])
        self.canvas.stroke()
        
        # Draw dashed overlay
        self.canvas.set_line_dash([5, 5])
        self.canvas.begin_path()
        self.canvas.move_to(edge.position[0], edge.position[1])
        self.canvas.line_to(edge.position[2], edge.position[3])
        self.canvas.stroke()
        self.canvas.set_line_dash([])

    def find_clicked_node(self, x, y):
        """Find node at click position"""
        for node in self.node_list:
            if math.sqrt((x - node.position[0])**2 + (y - node.position[1])**2) <= dot_width/2:
                return node
        return None
    def display(self):
        """Display all components"""
        return widgets.VBox([
            widgets.HBox([
                self.multi_canvas,
                self.bloch_output
            ]
            ),
            self.message_output,
            self.message_input,
            self.controls
        ], layout=widgets.Layout(align_items='center'))
    
    def setup_board_ipy(self):
        self.stroked_edge_list = []
        self.node_list = []
        self.edge_list =[]
        
        # Clear the canvas first
        self.canvas.clear()
        
        # Create nodes first
        with hold_canvas(self.canvas):
            # Create nodes
            for i in range(number_of_dots):
                for j in range(number_of_dots):
                    start_x = i * distance_between_dots + distance_between_dots/2
                    end_x = j * distance_between_dots + distance_between_dots/2
                    
                    # Create node object
                    node_id = f"{i}{j}"
                    node = Node(
                        id=node_id,
                        oval_id=f"node_{i}_{j}",
                        position=[start_x, end_x],
                        status=-1,
                        number_of_edges=0,
                        connections=[]
                    )
                    self.node_list.append(node)

            # Create edges between adjacent nodes
            for i in range(number_of_dots):
                for j in range(number_of_dots):
                    current_node = next(n for n in self.node_list if n.id == f"{i}{j}")
                    
                    # Create horizontal edge if not at last column
                    if j < number_of_dots - 1:
                        right_node = next(n for n in self.node_list if n.id == f"{i}{j+1}")
                        edge = Edge(
                            id=f"h_edge_{i}_{j}",
                            line_id=f"line_h_{i}_{j}",
                            line_id2=f"line_h2_{i}_{j}",
                            type=row,
                            position=[
                                current_node.position[0], current_node.position[1],
                                right_node.position[0], right_node.position[1]
                            ],
                            status=0,
                            nodes=[current_node.id, right_node.id]
                        )
                        self.stroked_edge_list.append(edge)
                        current_node.connections.append(edge.line_id)
                        right_node.connections.append(edge.line_id)

                    # Create vertical edge if not at last row
                    if i < number_of_dots - 1:
                        bottom_node = next(n for n in self.node_list if n.id == f"{i+1}{j}")
                        edge = Edge(
                            id=f"v_edge_{i}_{j}",
                            line_id=f"line_v_{i}_{j}",
                            line_id2=f"line_v2_{i}_{j}",
                            type=row,  # You might want to use a different type for vertical edges
                            position=[
                                current_node.position[0], current_node.position[1],
                                bottom_node.position[0], bottom_node.position[1]
                            ],
                            status=0,
                            nodes=[current_node.id, bottom_node.id]
                        )
                        self.stroked_edge_list.append(edge)
                        current_node.connections.append(edge.line_id)
                        bottom_node.connections.append(edge.line_id)

            # Draw grid lines
            self._draw_grid()
                
            # Draw edges
            for edge in self.stroked_edge_list:
                self._draw_edge(edge)
                
            # Draw nodes on top
            for node in self.node_list:
                self._draw_node(node)

        # Update adjacency matrix
        for node in self.node_list:
            self.find_adjacent_distances(node)

        return self.canvas
    def create_node_click_handler(self, node):
        """Create a click handler for a specific node"""
        def handler(x, y):
            # Check if click is within node bounds
            node_x, node_y = node.position
            if math.sqrt((x - node_x)**2 + (y - node_y)**2) <= dot_width/2:
                # Create a mock event object to maintain compatibility
                class MockEvent:
                    def __init__(self, x, y):
                        self.x = x
                        self.y = y
                
                self.node_click(MockEvent(x, y))
        return handler

    def update_node_color_ipy(self, node, color):
        """Update node color in ipycanvas"""
        with hold_canvas(self.canvas):
            self.canvas.fill_style = color
            self.canvas.stroke_style = color
            self.canvas.begin_path()
            self.canvas.arc(node.position[0], node.position[1], dot_width/2, 0, 2 * math.pi)
            self.canvas.fill()
            self.canvas.stroke()
        node.color = color

    def make_edge_between_nodes_ipy(self, clicked_node, adjacent_node):
        """Create edge between nodes in ipycanvas"""
        # Calculate start and end points
        start_x, start_y = clicked_node.position
        end_x, end_y = adjacent_node.position
        
        with hold_canvas(self.canvas):
            # Draw main line
            self.canvas.stroke_style = edge_color
            self.canvas.line_width = edge_width
            self.canvas.begin_path()
            self.canvas.move_to(start_x, start_y)
            self.canvas.line_to(end_x, end_y)
            self.canvas.stroke()
            
            # Draw dashed overlay
            self.canvas.set_line_dash([5, 5])  # Create dashed line effect
            self.canvas.stroke_style = edge_color
            self.canvas.begin_path()
            self.canvas.move_to(start_x, start_y)
            self.canvas.line_to(end_x, end_y)
            self.canvas.stroke()
            self.canvas.set_line_dash([])  # Reset dash pattern
        
        # Create edge object
        row_id = adjacent_node.id + clicked_node.id
        edge = Edge(
            row_id,
            f"line_{clicked_node.id}_{adjacent_node.id}",
            f"line_dashed_{clicked_node.id}_{adjacent_node.id}",
            row,
            [start_x, start_y, end_x, end_y],
            0,
            [adjacent_node.id, clicked_node.id]
        )
        self.edge_list.append(edge)
        self.include_edge_error(edge)
        self.update_node_color_ipy(adjacent_node, dot_selected_color)

    def get_mode(self):
        return self.mode
    
    def updateControls(self): 
        if self.mode == transmission:
            if self.continue_btn:
                self.continue_btn.layout.display='none'
            # start_transition_btn = Button(self.left_controls_frame, text = 'Generate key', command = self.callTransitionButtonClick)
            # start_transition_btn.grid(row=1, column=0, padx=5, sticky='W')
            # self.start_transition_btn = widgets.Button(description='Generate key')
            # self.start_transition_btn.on_click(self.callTransitionButtonClick)
            # self.start_transition_btn.layout = ''
            toggle_button(self.start_transition_btn)
            # back_btn = Button(self.right_controls_frame,text = 'Back', command = self.back)
            # back_btn.grid(row=1, column=2, padx=5, sticky='E')
            # replay_btn = Button(self.right_controls_frame,text = 'Replay', command = self.replay)
            # replay_btn.grid(row=1,column=3, padx=5, sticky='E')
        else:
            # self.continue_btn = Button(self.right_controls_frame, text = 'Continue to transmission Mode', command=self.switch_mode)
            # self.continue_btn.grid(row=1, column=0, sticky='E')
            self.continue_btn = widgets.Button(description='Continue to transmission Mode')
            self.continue_btn.on_click(self.switch_mode)
  
    def onHome(self):
        self.node_selection_counter = 0
        for edge in self.edge_list:
            self.canvas.delete(edge.line_id)
            self.canvas.delete(edge.line_id2)
        for node in self.node_list:
            self.update_node_color(node, dot_color)
        self.edge_list = []
        self.node_list = []
        self.qc = intialize_circuit(self.window)
        
        #self.window.destroy()
        # game_instance = Hom()
        # game_instance.mainloop()

    def delete_canvas(self):
        # self.canvas.delete('all')
        self.canvas.clear()
    
    def switch_mode(self, *args, **kwargs):
        if self.mode == transmission:
            self.mode = rearrange
        else:
            self.mode = transmission
        self.updateControls()
        for node in self.node_list:
            self.find_adjacent_distances(node)

    def submit(self, *args, **kwargs):
        global number_of_dots
        number_of_dots=self.grid_size_var.value
        global size_of_board
        size_of_board = number_of_dots * 100
        self.canvas_size = number_of_dots * 100
        self.delete_canvas()
        # path = os.path.dirname(__file__)
        # my_file = path+'/map2.jpeg'
        # img= ImageTk.PhotoImage(Image.open(my_file))    
        # self.canvas.create_image( 0, 0, image = img, anchor = "nw")
        # self.setup_board()
        # self.window.mainloop()
        self.draw()

    def reset(self, *args, **kwargs):
        self.delete_canvas()
        self.node_selection_counter=0
        # path = os.path.dirname(__file__)
        # my_file = path+'/map2.jpeg'
        # img= ImageTk.PhotoImage(Image.open(my_file))    
        # self.canvas.create_image( 0, 0, image = img, anchor = "nw")
        # self.setup_board()
        self.draw()
        # self.window.mainloop()
    
    def end_selection(self):
        end_node = next(x for x in self.node_list if x.id == self.edge_list[-1].nodes[1])
        self.update_node_color(end_node, dot_selected_color)
        [x.color != dot_selected_color and self.update_node_color(x, dot_disable_color) for x in self.node_list]

    def callTransitionButtonClick(self, *args, **kwargs):
        global replay_option
        replay_option = "Click_Button"
        self.transition()

    def callTransitionFromReplay(self):
        global replay_option
        replay_option = "Replay"
        self.transition()

    def callTransitionFromBack(self):
        global replay_option
        replay_option = "Back"
        self.transition()

    def BinarytoString(self, binary):  
        str_data =' '
        binary_data=''.join([str(item) for item in binary])
        str_data =  ''.join(chr(int(binary_data[i:i+8], 2)) for i in range(0, len(binary_data), 8))
        return str_data
    
    def perform_xor(self, a ,b):
        # Initialize the result string
        result = ""

        # Perform XOR operation on each bit
        for bit_a, bit_b in zip(a, b):
                if bit_a == bit_b:
                    result += "0"
                else:
                    result += "1"
        return result
    def send_message_classical(self, *args , **kwargs):
            if self.selectedtask.value == send_message_quantum:
                # print('quantum')
                binary_message = ''.join(format(ord(i), '08b') for i in self.message_var.get())
                decoded_message = threestage_message_transmission(binary_message)
                self.decoded_message = self.BinarytoString(decoded_message)
                sent_label = Label(self.left_controls_frame, text = 'Message sent from Alice: '+self.message_var.get())
                sent_label.grid(row=6,column=0, padx=5, sticky='W')
                recieved_label = Label(self.left_controls_frame, text = 'Message Recieved to Bob: '+self.decoded_message)
                recieved_label.grid(row=7,column=0, padx=5, sticky='W')
            else:
                binary_message = ''.join(format(ord(i), '08b') for i in self.message_entry.value)
                key_message = self.key_generated
                # key_message = ''.join(map(str, key_message))
                # Pad the second string to match the length of the first string
                key_message = key_message.zfill(len(binary_message))
                encoded_message = self.perform_xor(binary_message, key_message)
                decoded_message = self.perform_xor(key_message, encoded_message)
                # print('message after decoding',decoded_message)
                # print('message after conversion', self.BinarytoString(decoded_message))
                self.decoded_message = self.BinarytoString(decoded_message)
                # sent_label = Label(self.left_controls_frame, text = 'Message sent from Alice: '+self.message_var.get())
                # sent_label = widgets.Label(value=)
                # with self.message_output:
                #     print(f'Message sent from Alice: {self.message_entry.value}')
                self.message_output.append_display_data(f'Message sent from Alice: {self.message_entry.value}')
                # sent_label.grid(row=6,column=0, padx=5, sticky='W')
                # recieved_label = Label(self.left_controls_frame, text = 'Message Recieved to Bob: '+self.decoded_message)
                # recieved_label.grid(row=7,column=0, padx=5, sticky='W')
                # recieved_label = widgets.Label(value=)

                # with self.message_output:
                #     print(f"Message Received to Bob: {self.decoded_message}")
                # display(widgets.VBox([sent_label, recieved_label]))
                self.message_output.append_display_data(f"Message Received to Bob: {self.decoded_message}")

    def ball_movement(self, edge_coords, start_node):
        channel_count = 0
        channel_order_temp = channel_order[::-1] if replay_option == "Back" else channel_order
        
        setGlobalValues(channel_order_temp, channel_count, self.bloch_output)
        ball_coords = [edge_coords[0], edge_coords[1]]
        end_ball_coords = [edge_coords[2], edge_coords[3]]
        
        if start_node != ball_coords:
            end_ball_coords = ball_coords
            ball_coords = [edge_coords[2], edge_coords[3]]

        
        ydiff = end_ball_coords[1] - ball_coords[1]
        xdiff = end_ball_coords[0] - ball_coords[0]
        xdiff = 0.1 if xdiff == 0 else xdiff
        slope = ydiff / xdiff
        i = 0
        
        def draw_ball(x, y):
            with hold_canvas(self.ball_canvas):
                # Clear the ball canvas
                self.ball_canvas.clear()
                
                # Draw new ball
                self.ball_canvas.fill_style = qbit_color
                self.ball_canvas.stroke_style = qbit_color
                self.ball_canvas.begin_path()
                self.ball_canvas.arc(x, y, 5, 0, 2 * math.pi)
                self.ball_canvas.fill()
                self.ball_canvas.stroke()
        
        def animate_ball():
            nonlocal i, ball_coords, channel_count
            
            while ball_coords != end_ball_coords:
                if channel_count == 0:
                    channel_count = periodic_update()
                
                time.sleep(0.1)
                
                i += 1
                yinc = round(0 if slope == 0 else ydiff * (i / 100))
                xinc = round(xdiff * (i / 100) if slope == 0 else yinc / slope)
                
                # Update ball position
                if xinc < 0 and ball_coords[0] < end_ball_coords[0] or xinc > 0 and ball_coords[0] > end_ball_coords[0]:
                    ball_coords[0] = end_ball_coords[0]
                else:
                    ball_coords[0] += xinc
                    
                if yinc < 0 and ball_coords[1] < end_ball_coords[1] or yinc > 0 and ball_coords[1] > end_ball_coords[1]:
                    ball_coords[1] = end_ball_coords[1]
                else:
                    ball_coords[1] += yinc
                
                # Draw ball at new position
                draw_ball(ball_coords[0], ball_coords[1])
        
        # Display the ball canvas
        # display(ball_canvas)
        
        # Run the animation
        animate_ball()
        
        # Clean up by clearing the ball canvas
        self.ball_canvas.clear()

    def transition(self):
        global gate_count, gate_order, channel_order, channel_count, replay_option
        self.end_selection()
        json_String = self.convertToJson(self.edge_list)
        # print(json_String)
        #print(self.edge_list)
        # print(self.ksu_id_var.get())
        # self.message_var=StringVar()
        # message_label = widgets.Label(value = 'Enter a message to communicate:')
        # self.message_entry = widgets.Text()
        # # message_label.grid(row=4,column=0, padx=5, sticky='W')
        # # message_entry.grid(row=4,column=1, padx=5, sticky='W')
        # send_message_button = widgets.Button(description = 'Send Message')
        # send_message_button.on_click(self.send_message_classical)

        # display(widgets.HBox([message_label, self.message_entry, send_message_button]))
        toggle_button(self.message_input)
        # send_message_button.grid(row=4,column=2, padx=5, sticky='W')
        if self.protocol == E91:
                self.key_generated = building_circuit(self.node_selection_counter, self.display_frame)
        else:
                self.key_generated = threestage_key_generation(self.node_selection_counter)
                # r6 = Radiobutton(self.left_controls_frame, text='Send a Message via Classical Channel', value= send_message, variable=self.selectedtask)
                r6 = widgets.RadioButtons(
                    options=['Send a Message via Classical Channel', 'Send a Message via Quantum Channel'],
                    description='Task:',
                    disabled=False
                )
                # r7 = Radiobutton(self.left_controls_frame, text='Send a Message via Quantum Channel', value= send_message_quantum, 
                #          variable=self.selectedtask)
                r7 = widgets.RadioButtons(
                    options=['Send a Message via Classical Channel', 'Send a Message via Quantum Channel'],
                    description='Task:',
                    disabled=False
                )
                # r6.grid(row=5, column=0,padx=5,sticky='W')
                # r7.grid(row=5, column=1,padx=5,sticky='W')

        # else:
        #     if self.protocol == ThreeStage:
        #         binary_message = ''.join(format(ord(i), '08b') for i in self.message)
        #         threestage_message_transmission(binary_message)

        # for i in range(len(self.edge_list)):
        #     edge_coords = self.canvas.coords(self.edge_list[i].line_id)
        #     start_node = next(x for x in self.node_list if x.id == self.edge_list[i].nodes[0]).position
        #     self.ball_movement(edge_coords, start_node)
        
        # if self.protocol == ThreeStage:
        #     for i in range(len(self.edge_list)):
        #         edge_coords = self.canvas.coords(self.edge_list[len(self.node_list)-i].line_id)
        #         start_node = next(x for x in self.node_list if x.id == self.edge_list[len(self.node_list)-i].nodes[0]).position
        #         self.ball_movement(edge_coords, start_node)
        #     for i in range(len(self.edge_list)):
        #         edge_coords = self.canvas.coords(self.edge_list[i].line_id)
        #         start_node = next(x for x in self.node_list if x.id == self.edge_list[i].nodes[0]).position
        #         self.ball_movement(edge_coords, start_node)


        # Animate ball movement for each edge
        for edge in self.edge_list:
            # Get edge coordinates directly from the Edge object
            edge_coords = edge.position  # This should contain [start_x, start_y, end_x, end_y]
            start_node = next(x for x in self.node_list if x.id == edge.nodes[0]).position
            self.ball_movement(edge_coords, start_node)
        
        if self.protocol == ThreeStage:
            # Reverse path
            for i in range(len(self.edge_list) - 1, -1, -1):
                edge = self.edge_list[i]
                edge_coords = edge.position
                start_node = next(x for x in self.node_list if x.id == edge.nodes[0]).position
                self.ball_movement(edge_coords, start_node)
            
            # Forward path again
            for edge in self.edge_list:
                edge_coords = edge.position
                start_node = next(x for x in self.node_list if x.id == edge.nodes[0]).position
                self.ball_movement(edge_coords, start_node)
            
        # if self.selectedtask == send_message:
        #     if self.protocol == E91:
        #         self.message_transmission(self.node_selection_counter)
        #     # else:
        #     #     self.message_transmission(2)
        # self.node_selection_counter = 0        
        # if(replay_option == "Click_Button"):
        #     insert(json_String, self.ksu_id_var)

    def replay(self):
        global replay_option
        replay_option = "Replay"
        rows = select(self.ksu_id_var)
        # print(rows)
        results = json.loads((rows[0])[0])
        # print(len(results))
        self.edge_list = []
        self.edge_list_temp = []
        for result in results:
            nodes = result['_nodes']
            start_node = next(x for x in self.node_list if x.id == nodes[1])
            end_node = next(x for x in self.node_list if x.id == nodes[0])
            self.make_edge_between_nodes(start_node, end_node)
        # print(self.edge_list)
        start(self.bloch_output)
        self.callTransitionFromReplay()

    def back(self):
        self.edge_list_temp = self.edge_list
        if(len(self.edge_list) > 0):
            result = self.edge_list[len(self.edge_list) - 1]
            self.edge_list = []
            if(isinstance(result, Edge)):
                nodes = result.nodes
            start_node = next(x for x in self.node_list if x.id == nodes[0])
            end_node = next(x for x in self.node_list if x.id == nodes[1])
            self.make_edge_between_nodes(start_node, end_node)
            self.callTransitionFromBack()
        self.edge_list = self.edge_list_temp

    def find_adjacent_distances(self, selected_node):
        [r,c] = [int(selected_node.id[0]), int(selected_node.id[1])]
        for nodeid in [str(r)+str(c-1), str(r)+str(c+1), str(r-1)+str(c), str(r+1)+str(c)]:
            adjacent_node = next((x for x in self.node_list if x.id == nodeid), 0)
            if adjacent_node:
                [ar,ac] = [int(nodeid[0]), int(nodeid[1])]
                distance = math.dist(selected_node.position, adjacent_node.position)
                self.adjacency_matrix[ar*(number_of_dots)+ac][r*(number_of_dots)+c]=distance
                self.adjacency_matrix[r*(number_of_dots)+c][ar*(number_of_dots)+ac]=distance

    def setup_board(self):
        self.edge_list =[]
        self.node_list =[]
        for i in range(number_of_dots):
            for j in range(number_of_dots):
                start_x = i*distance_between_dots+distance_between_dots/2
                end_x = j*distance_between_dots+distance_between_dots/2
                id1 = 0
                id2 = 0
                if j != number_of_dots-1:
                    id1 = self.canvas.create_line(start_x, end_x, start_x, end_x+distance_between_dots, fill='black', width=2, dash = (2, 2))
                if i != number_of_dots-1:
                    id2 = self.canvas.create_line(start_x, end_x,start_x+distance_between_dots, end_x, fill='black', width=2, dash=(2, 2))
                oval_id = self.canvas.create_oval(start_x-dot_width/2, end_x-dot_width/2, start_x+dot_width/2, end_x+dot_width/2, fill=dot_color, outline=dot_color)
                node = Node(str(i)+str(j), oval_id, [start_x, end_x], -1, 0, [id1, id2])
                dnd = DragManager(self.get_mode)
                dnd.add_dragable(node, self.canvas)
                self.canvas.tag_bind(oval_id, f"<Button-1>", self.node_click)
                self.node_list.append(node)
        for node in self.node_list:
            id = node.id
            self.find_adjacent_distances(node)
            if int(id[0]) > 0:
                up_node = next(x for x in self.node_list if x.id == str(int(id[0])-1)+str(id[1]))
                node.connections_update(up_node.connections[1])
            if int(id[1]) > 0:
                left_node = next(x for x in self.node_list if x.id == str(id[0])+str(int(id[1])-1))
                node.connections_update(left_node.connections[0])

    def mainloop(self):
        self.window.mainloop()
    
    def compare_node_width(self,node, position):
        x_start_position = node.position[0]-dot_width
        x_end_position = node.position[0]+dot_width
        y_start_position = node.position[1]-dot_width
        y_end_position = node.position[1]+dot_width
        return x_start_position < position[0] and x_end_position > position[0] and y_start_position <position[1] and y_end_position > position[1]

    def convert_grid_to_logical_position(self, grid_position): 
        clicked_node = next(x for x in self.node_list if self.compare_node_width(x, grid_position))
        return clicked_node
    
    def update_node_color(self, node, dot_color):
        """Update node color in ipycanvas"""
        with hold_canvas(self.canvas):
            self.canvas.fill_style = dot_color
            self.canvas.stroke_style = dot_color
            self.canvas.begin_path()
            self.canvas.arc(node.position[0], node.position[1], dot_width/2, 0, 2 * math.pi)
            self.canvas.fill()
            self.canvas.stroke()
        node.color = dot_color
        
        # Redraw on top of other elements (equivalent to tag_raise)
        self.canvas.draw_image(self.canvas, 0, 0)

    def include_edge_error(self, edge):
        if edge.id == 2:
            self.canvas.after(3000, self.canvas.delete, edge.line_id)
            self.canvas.after(6000, lambda:self.delete_edge(edge))
            #self.row_status[edge.position[1]][edge.position[0]] = 0
        
    def update_node_selection(self, clicked_node):
        # make all node colours to disable except already selected nodes
        [x.color != dot_selected_color and self.update_node_color(x, dot_disable_color) for x in self.node_list]
        # make selection status to 1 for initial selection else +1 as new edge will be created and update selection color
        clicked_node.prev_selection_status = True
        if clicked_node.status > 0:
            clicked_node.status += 1
        else:
            clicked_node.status = 0
            self.update_node_color(clicked_node, dot_selection_color)
        # if self.protocol == E91:
        #     create_circuit()
        # update adjacent nodes selection status and colors    
        [r,c] = [int(clicked_node.id[0]), int(clicked_node.id[1])]
        for nodeid in [str(r)+str(c-1), str(r)+str(c+1), str(r-1)+str(c), str(r+1)+str(c)]:
            adjacent_node = next((x for x in self.node_list if x.id == nodeid), 0)
            if adjacent_node and adjacent_node.status <= 0:
                adjacent_node.color != dot_selected_color and self.update_node_color(adjacent_node, dot_color)
                adjacent_node.status = 0

    def delete_edge(self,edge):
        self.canvas.delete(edge.line_id2)
        node2 = str(int(edge.position[0])+1)+str(edge.position[1]) if edge.type == row else str(edge.position[0])+str(int(edge.position[1])+1)
        node_id = [str(edge.position[0])+str(edge.position[1]), node2]
        for node in self.node_list:
            if node.id in node_id:
               node.edges-=1
               if node.edges < 1 and node.color != dot_selection_color:
                   self.update_node_color(node, dot_disable_color)
        
    def find_adjecent_selected_node(self, clicked_node):
        [r,c] = [int(clicked_node.id[0]), int(clicked_node.id[1])]
        for nodeid in [str(r)+str(c-1), str(r)+str(c+1), str(r-1)+str(c), str(r+1)+str(c)]:
            adjacent_node = next((x for x in self.node_list if x.id == nodeid), 0)
            if adjacent_node and adjacent_node.prev_selection_status:
                return adjacent_node
            
    def get_edge_connection(self, clicked_node, adjacent_node):
        for node_connection in clicked_node.connections:
            if node_connection and node_connection in adjacent_node.connections:
                return node_connection
            
    def make_edge_between_nodes(self, clicked_node, adjacent_node):
        """Create edge between nodes in ipycanvas"""
        # Get start and end coordinates from node positions
        start_x, start_y = clicked_node.position
        end_x, end_y = adjacent_node.position
        
        with hold_canvas(self.canvas):
            # Draw main line
            self.canvas.stroke_style = edge_color
            self.canvas.line_width = edge_width
            self.canvas.begin_path()
            self.canvas.move_to(start_x, start_y)
            self.canvas.line_to(end_x, end_y)
            self.canvas.stroke()
            
            # Draw dashed overlay
            self.canvas.set_line_dash([5, 5])  # Create dashed line effect
            self.canvas.stroke_style = edge_color
            self.canvas.begin_path()
            self.canvas.move_to(start_x, start_y)
            self.canvas.line_to(end_x, end_y)
            self.canvas.stroke()
            self.canvas.set_line_dash([])  # Reset dash pattern
        
        # Create edge object with unique IDs for the lines
        line_id = f"line_{clicked_node.id}_{adjacent_node.id}"
        line_id2 = f"line_dashed_{clicked_node.id}_{adjacent_node.id}"
        row_id = adjacent_node.id + clicked_node.id
        
        edge = Edge(
            row_id, 
            line_id,
            line_id2, 
            row, 
            [start_x, start_y, end_x, end_y],
            0,
            [adjacent_node.id, clicked_node.id]
        )
        
        self.edge_list.append(edge)
        self.include_edge_error(edge)
        self.update_node_color(adjacent_node, dot_selected_color)

    def update_nodes(self, clicked_node):
        if clicked_node.status == 0:
            adjacent_node = self.find_adjecent_selected_node(clicked_node)
            #make edges
            self.make_edge_between_nodes(clicked_node, adjacent_node)
        self.update_node_selection(clicked_node)
        if (len(self.edge_list)) == 0:
            start(self.bloch_output)
    
    def minDistance(self, dist, sptSet):
        min = 1e7
        for v in range(number_of_dots*number_of_dots):
            if dist[v] < min and sptSet[v] == False:
                min = dist[v]
                min_index = v
        return min_index
        
    def dijkstra(self, src, destination):
        dist = [1e7] *number_of_dots*number_of_dots
        dist[src] = 0
        sptSet = [False] * number_of_dots*number_of_dots
        pathSet = []
 
        for cout in range(number_of_dots*number_of_dots):
            u = self.minDistance(dist, sptSet)
            sptSet[u] = True
            for v in range(number_of_dots*number_of_dots):
                if (self.adjacency_matrix[u][v] > 0 and
                   sptSet[v] == False and
                   dist[v] > dist[u] + self.adjacency_matrix[u][v]):
                    pathSet.append([v,u])
                    dist[v] = dist[u] + self.adjacency_matrix[u][v]
        dest = destination
        path = [destination]
        while(dest != src):
            dest = next(x[1] for x in reversed(pathSet) if x[0] == dest)
            path.append(dest)
        return path[::-1]
    
    def message_transmission(self, shortest_node_path_length):
        binary_message = ''.join(format(ord(i), '08b') for i in self.message)
        recieved_message = transmit_message(shortest_node_path_length, binary_message, self.bloch_output)
        #return ''.join(chr(int(recieved_message[i:i+8], 2)) for i in range(0, len(recieved_message), 8))
    
    # def generate_secure_key(self, shortest_node_path):
    #     #print('here')
        
    def e91_node_click(self, clicked_node):
        [r,c] = [int(clicked_node.id[0]), int(clicked_node.id[1])]
        if self.node_selection_counter == 0:
            self.first_node_selected = r*number_of_dots+c
        elif self.node_selection_counter == 1:
            shortest_node_path = self.dijkstra(self.first_node_selected,r*number_of_dots+c)
            self.node_selection_counter = len(shortest_node_path)-1
            print(self.node_selection_counter)
            for i,n in enumerate(shortest_node_path):
                if i > 0:
                    [r,c] = [n//number_of_dots, n%number_of_dots]
                    first_node = next(x for x in self.node_list if x.id == str(r)+str(c))
                    n2 = shortest_node_path[i-1]
                    [r1,c1] = [n2//number_of_dots, n2%number_of_dots]
                    second_node = next(x for x in self.node_list if x.id == str(r1)+str(c1))
                    self.make_edge_between_nodes(first_node, second_node)
            # if self.selectedtask == send_message:
            #     print(shortest_node_path)
            #     self.message_transmission(shortest_node_path)
            # else:
            # self.generate_secure_key(shortest_node_path)
            #create_entangled_qubits(self.qc, len(shortest_node_path)-1)

        if (len(self.edge_list)) == 0:
            start(self.bloch_output)
        self.update_node_color(clicked_node, dot_selected_color)
        

    def node_click(self, event):
        event_position = [event.x, event.y]
        clicked_node = self.convert_grid_to_logical_position(event_position)

        if self.mode == transmission:
            if self.protocol == E91:
                self.e91_node_click(clicked_node)
            else:
                self.update_nodes(clicked_node)
            self.node_selection_counter += 1

    def convertToJson(self, edge_list):
        json_String = "["
        for i in edge_list:
            json_String = json_String + i.to_json()
            json_String = json_String + ","
        json_String = json_String[:-1] + "]"
        return json_String
    

if __name__ == '__main__':
    display(Quantum_Network(transmission,E91 , "asdasd", "123").display())