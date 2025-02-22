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
from PIL import Image,ImageTk
from Utils import start, setGlobalValues, periodic_update
from dto.dto import insert, select, fetchallRows
from Quantum_Circuits import *


class Quantum_Network():
    def __init__(self, homeSelf):
        self.window = Tk()
        self.window.title('Quantum Key Distribution Network') 
        self.canvas_size = size_of_board
        self.mode = homeSelf.selectedMode.get()
        self.protocol = homeSelf.selectedProtocol.get()
        self.selectedtask = StringVar()
        self.selectedtask.set(send_message)
        self.window.state('zoomed')
        self.message_var=StringVar()
        self.continue_btn = 0
        self.node_selection_counter = 0
        self.key_generated = False
        self.first_node_selected = 0
        self.adjacency_matrix =  [[0 for col in range(number_of_dots*number_of_dots)] for row in range(number_of_dots*number_of_dots)]

        # Create Frames
        self.grid_frame = Frame(self.window, width= self.canvas_size+500, height=self.canvas_size+100)
        self.grid_frame.grid(row=0, column=0, padx=10, pady=10)

        self.display_frame = Frame(self.window, width= self.canvas_size+100, height=self.canvas_size+100)
        self.display_frame.grid(row=0, column=4, padx=10, pady=10)

        self.controls_frame = Frame(self.window, width=self.canvas_size+500, height=200)
        self.controls_frame.grid(row=1, column=0, padx=10, pady=10, sticky='W')

        self.canvas = Canvas(self.grid_frame, width=self.canvas_size+300, height=self.canvas_size+100)
        self.canvas.pack(fill = "both", expand = True)
        path = os.path.dirname(__file__)
        my_file = path+'/map2.jpeg'
        img= ImageTk.PhotoImage(Image.open(my_file))    
        self.canvas.create_image( 0, 0, image = img, anchor = "nw")

        self.left_controls_frame = Frame(self.controls_frame)
        self.left_controls_frame.grid(column=0, row=0, sticky="NW")

        self.right_controls_frame = Frame(self.controls_frame)
        self.right_controls_frame.grid(column=1, row=0, sticky="NE")

        self.setup_board()
        self.grid_size_var=IntVar()
        self.grid_size_var.set(5)
        self.qc = intialize_circuit(self.window)
        
        
        self.switch_btn_text = 'Switch to arrangement mode'

        name_label = Label(self.left_controls_frame, text = 'Enter the grid size (max value 5) :')
        name_entry = Entry(self.left_controls_frame,textvariable = self.grid_size_var)
        sub_btn=Button(self.left_controls_frame,text = 'Submit', command = self.submit)

        reset_btn = Button(self.right_controls_frame,text = 'Reset', command = self.reset)

        name_label.grid(row=0,column=0, padx=5, sticky='W')
        name_entry.grid(row=0,column=1, padx=5, sticky='W')
        sub_btn.grid(row=0,column=2, padx= 5, sticky='W')

        reset_btn.grid(row=0, column=0, padx=5, sticky='E')
        self.updateControls()
        self.window.mainloop()
    
    def get_mode(self):
        return self.mode
    
    def updateControls(self): 
        if self.mode == transmission:
            if self.continue_btn:
                self.continue_btn.destroy()
            start_transition_btn = Button(self.left_controls_frame, text = 'Generate key', command = self.callTransitionButtonClick)
            start_transition_btn.grid(row=1, column=0, padx=5, sticky='W')
        else:
            self.continue_btn = Button(self.right_controls_frame, text = 'Continue to transmission Mode', command=self.switch_mode)
            self.continue_btn.grid(row=1, column=0, sticky='E')
        

    def delete_canvas(self):
        self.canvas.delete('all')
    
    def switch_mode(self):
        if self.mode == transmission:
            self.mode = rearrange
        else:
            self.mode = transmission
        self.updateControls()
        for node in self.node_list:
            self.find_adjacent_distances(node)

    def submit(self):
        global number_of_dots
        number_of_dots=self.grid_size_var.get()
        global size_of_board
        size_of_board = number_of_dots * 100
        self.canvas_size = number_of_dots * 100
        self.delete_canvas()
        path = os.path.dirname(__file__)
        my_file = path+'/map2.jpeg'
        img= ImageTk.PhotoImage(Image.open(my_file))    
        self.canvas.create_image( 0, 0, image = img, anchor = "nw")
        self.setup_board()
        self.window.mainloop()

    def reset(self):
        global number_of_dots
        number_of_dots=self.grid_size_var.get()
        global size_of_board
        size_of_board = number_of_dots * 100
        self.canvas_size = number_of_dots * 100
        self.delete_canvas()
        self.node_list = []
        self.edge_list = []
        self.node_selection_counter=0
        self.key_generated = ''
        self.decoded_message = ''
        path = os.path.dirname(__file__)
        my_file = path+'/map2.jpeg'
        img= ImageTk.PhotoImage(Image.open(my_file))    
        self.canvas.create_image( 0, 0, image = img, anchor = "nw")
        self.setup_board()
        self.window.mainloop()
    
    def end_selection(self):
        end_node = next(x for x in self.node_list if x.id == self.edge_list[-1].nodes[1])
        self.update_node_color(end_node, dot_selected_color)
        [x.color != dot_selected_color and self.update_node_color(x, dot_disable_color) for x in self.node_list]

    def callTransitionButtonClick(self):
        global replay_option
        replay_option = "Click_Button"
        self.transition()

    def BinarytoString(self, binary):  
        str_data =' '
        binary_data=''.join([str(item) for item in binary])
        str_data =  ''.join(chr(int(binary_data[i:i+8], 2)) for i in range(0, len(binary_data), 8))
        return str_data
    
    def perform_xor(self, a ,b):
        result = ""
        for bit_a, bit_b in zip(a, b):
                if bit_a == bit_b:
                    result += "0"
                else:
                    result += "1"
        return result
    
    def send_message_classical(self):
            if self.selectedtask.get() == send_message_quantum:
                sent_label = Label(self.left_controls_frame, text = 'Message sent from Alice: '+self.message_var.get())
                sent_label.grid(row=6,column=0, padx=5, sticky='W')
                binary_message = ''.join(format(ord(i), '08b') for i in self.message_var.get())
                encoded_label = Label(self.left_controls_frame, text = 'ASCII for message('+self.message_var.get()+ '): '+binary_message)
                encoded_label.grid(row=7,column=0, padx=5, sticky='W')
                decoded_message = threestage_message_transmission(binary_message)
                encoding_label = Label(self.left_controls_frame, text = 'Encoded message using Z-basis')
                encoding_label.grid(row=8,column=0, padx=5, sticky='W')
                decoding_label = Label(self.left_controls_frame, text = 'Qubits Measurement Completed')
                decoding_label.grid(row=9,column=0, padx=5, sticky='W')
                self.decoded_message = self.BinarytoString(decoded_message)
                recieved_label = Label(self.left_controls_frame, text = 'Message Recieved to Bob: '+self.decoded_message)
                recieved_label.grid(row=10,column=0, padx=5, sticky='W')
            else:
                binary_message = ''.join(format(ord(i), '08b') for i in self.message_var.get())
                sent_label = Label(self.left_controls_frame, text = 'Message sent from Alice: '+self.message_var.get())
                sent_label.grid(row=6,column=0, padx=5, sticky='W')
                key_message = self.key_generated
                key_message = key_message.zfill(len(binary_message))
                encoded_ASCII_label = Label(self.left_controls_frame, text = 'ASCII for message('+self.message_var.get()+ '): '+binary_message)
                encoded_ASCII_label.grid(row=7,column=0, padx=5, sticky='W')
                encoded_message = self.perform_xor(binary_message, key_message)
                encoded_label = Label(self.left_controls_frame, text = 'Encoded message for message('+self.message_var.get()+ '): '+encoded_message)
                encoded_label.grid(row=8,column=0, padx=5, sticky='W')
                decoded_message = self.perform_xor(key_message, encoded_message)
                self.decoded_message = self.BinarytoString(decoded_message)

                recieved_label = Label(self.left_controls_frame, text = 'Message Recieved to Bob: '+self.decoded_message)
                recieved_label.grid(row=9,column=0, padx=5, sticky='W')

    def ball_movement(self,edge_coords, start_node ):
            channel_count = 0
            channel_order_temp = None
            # if replay_option == "Back":
            #     channel_order_temp = channel_order[::-1]

            channel_order_temp = channel_order
            setGlobalValues(channel_order_temp, channel_count, self.window)
            ball_coords = [edge_coords[0], edge_coords[1]]
            end_ball_coords = [edge_coords[2], edge_coords[3]]
            if start_node != ball_coords:
                end_ball_coords = ball_coords
                ball_coords = [edge_coords[2],edge_coords[3]]
            ball = self.canvas.create_oval(ball_coords[0],ball_coords[1],ball_coords[0],ball_coords[1], fill=qbit_color, outline=qbit_color, width=10)
            ydiff = end_ball_coords[1] - ball_coords[1]
            xdiff = end_ball_coords[0] - ball_coords[0]
            xdiff = 0.1 if xdiff == 0 else xdiff
            slope = ydiff / xdiff
            i=0
            while ball_coords != end_ball_coords:
                if(channel_count == 0):
                    channel_count = periodic_update()
                time.sleep(0.1)
                xinc = 0
                yinc = 0
                i+=1
                yinc = round(0 if slope == 0  else ydiff * (i / 100))
                xinc = round(xdiff * (i / 100) if slope == 0 else yinc / slope)
                ball_coords[0] += xinc
                ball_coords[1] += yinc
                if xinc < 0 and ball_coords[0] < end_ball_coords[0] or xinc > 0 and ball_coords[0] > end_ball_coords[0]:
                    ball_coords[0] -= xinc
                    xinc =  end_ball_coords[0]-ball_coords[0]
                    ball_coords[0] = end_ball_coords[0]
                if yinc < 0 and ball_coords[1] < end_ball_coords[1] or yinc > 0 and ball_coords[1] > end_ball_coords[1]:
                    ball_coords[1] -= yinc
                    yinc =  end_ball_coords[1]-ball_coords[1]
                    ball_coords[1] = end_ball_coords[1]
                self.canvas.move(ball,xinc,yinc)
                self.canvas.update()
            self.canvas.delete(ball)

    def transition(self):
        global gate_count, gate_order, channel_order, channel_count, replay_option
        self.end_selection()
        for i in range(len(self.edge_list)):
            edge_coords = self.canvas.coords(self.edge_list[i].line_id)
            start_node = next(x for x in self.node_list if x.id == self.edge_list[i].nodes[0]).position
            self.ball_movement(edge_coords, start_node)
        
        if self.protocol == ThreeStage:
            for i in range(len(self.edge_list)):
                edge_coords = self.canvas.coords(self.edge_list[len(self.edge_list)-1-i].line_id)
                start_node = next(x for x in self.node_list if x.id == self.edge_list[len(self.edge_list)-1-i].nodes[1]).position
                self.ball_movement(edge_coords, start_node)
            for i in range(len(self.edge_list)):
                edge_coords = self.canvas.coords(self.edge_list[i].line_id)
                start_node = next(x for x in self.node_list if x.id == self.edge_list[i].nodes[0]).position
                self.ball_movement(edge_coords, start_node)

        
        message_label = Label(self.left_controls_frame, text = 'Enter a message to communicate:')
        message_entry = Entry(self.left_controls_frame,textvariable = self.message_var)
        message_label.grid(row=5,column=0, padx=5, sticky='W')
        message_entry.grid(row=5,column=1, padx=5, sticky='W')
        send_message_button = Button(self.left_controls_frame,text = 'Send Message', command = self.send_message_classical)
        send_message_button.grid(row=5,column=2, padx=5, sticky='W')

        if self.protocol == E91:
                self.key_generated = building_circuit(self.node_selection_counter, self.display_frame)
        else:
                self.key_generated = threestage_key_generation(self.node_selection_counter)
                r6 = Radiobutton(self.left_controls_frame, text='Send a Message via Classical Channel', value= send_message, variable=self.selectedtask)
                r7 = Radiobutton(self.left_controls_frame, text='Send a Message via Quantum Channel', value= send_message_quantum, 
                         variable=self.selectedtask)
                r6.grid(row=4, column=0,padx=5,sticky='W')
                r7.grid(row=4, column=1,padx=5,sticky='W')

        if self.key_generated: 
            key_generated_label = Label(self.left_controls_frame, text = 'key generated: '+self.key_generated)
            key_generated_label.grid(row=1,column=1, padx=5, sticky='W')


            

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
        self.canvas.itemconfig(node.oval_id, fill= dot_color, outline= dot_color )
        node.color = dot_color
        self.canvas.tag_raise(node.oval_id)

    def include_edge_error(self, edge):
        if edge.id == 2:
            self.canvas.after(3000, self.canvas.delete, edge.line_id)
            self.canvas.after(6000, lambda:self.delete_edge(edge))
        
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
        node_connection = self.get_edge_connection(clicked_node, adjacent_node)
        [sx, sy, ex, ey] = self.canvas.coords(node_connection)
        line_id = self.canvas.create_line(sx, sy, ex, ey, fill=edge_color, width=edge_width)
        line_id2 = self.canvas.create_line(sx, sy, ex, ey, fill=edge_color, width=edge_width, dash=(2,2))
        row_id = adjacent_node.id+clicked_node.id
        edge = Edge(row_id, line_id, line_id2, row, [sx, sy, ex, ey], 0, [adjacent_node.id, clicked_node.id] )
        self.edge_list.append(edge)
        # self.include_edge_error(edge)
        self.update_node_color(adjacent_node, dot_selected_color)

    def update_nodes(self, clicked_node):
        if clicked_node.status == 0:
            adjacent_node = self.find_adjecent_selected_node(clicked_node)
            #make edges
            self.make_edge_between_nodes(clicked_node, adjacent_node)
        self.update_node_selection(clicked_node)
        if (len(self.edge_list)) == 0:
            start(self.window)
    
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
        
    def e91_node_click(self, clicked_node):
        [r,c] = [int(clicked_node.id[0]), int(clicked_node.id[1])]
        if self.node_selection_counter == 0:
            self.first_node_selected = r*number_of_dots+c
            if (len(self.edge_list)) == 0:
                start(self.window)
            self.update_node_color(clicked_node, dot_selected_color)
        elif self.node_selection_counter == 1:
            shortest_node_path = self.dijkstra(self.first_node_selected,r*number_of_dots+c)
            self.node_selection_counter = len(shortest_node_path)-1
            for i,n in enumerate(shortest_node_path):
                if i > 0:
                    [r,c] = [n//number_of_dots, n%number_of_dots]
                    first_node = next(x for x in self.node_list if x.id == str(r)+str(c))
                    n2 = shortest_node_path[i-1]
                    [r1,c1] = [n2//number_of_dots, n2%number_of_dots]
                    second_node = next(x for x in self.node_list if x.id == str(r1)+str(c1))
                    self.make_edge_between_nodes(first_node, second_node)
                    if (len(self.edge_list)) == 0:
                        start(self.window)
                    self.update_node_color(clicked_node, dot_selected_color)
            self.end_selection()
            

    def node_click(self, event):
        event_position = [event.x, event.y]
        clicked_node = self.convert_grid_to_logical_position(event_position)
        if self.mode == transmission:
            if self.protocol == E91:
                self.e91_node_click(clicked_node)
            else:
                self.update_nodes(clicked_node)
            self.node_selection_counter += 1
