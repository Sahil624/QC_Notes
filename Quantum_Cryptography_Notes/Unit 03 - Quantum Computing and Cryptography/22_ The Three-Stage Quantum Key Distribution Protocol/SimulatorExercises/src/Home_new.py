import ipywidgets as widgets
from IPython.display import display
from global_variables import *
from QuantumNetwork_new import Quantum_Network as QNetwork

class Home:
    def disable_multiple_radiobuttons(self, e):
        print(e)
        if self.selectedProtocol == ThreeStage:
            e.disabled = True

    def __init__(self):
        self.window = widgets.Output()
        self.page = 1
        
        # Title
        title = widgets.HTML(value="<h2>Welcome !!!</h2>")
        
        # Student ID
        self.ksu_id_var = widgets.Text(
            description='Enter your Student ID:',
            style={'description_width': 'initial'}
        )
        
        # Mode Selection
        mode_label = widgets.HTML(value="<b>Select the mode:</b>")
        self.selectedMode = widgets.RadioButtons(
            options=[('Transmission Mode', transmission), 
                    ('Arrangement Mode', rearrange)],
            value=transmission
        )
        
        # Protocol Selection
        protocol_label = widgets.HTML(value="<b>Select the Quantum Network Protocol:</b>")
        self.selectedProtocol = widgets.RadioButtons(
            options=[('E91 Protocol', E91),
                    ('3-Stage Protocol', ThreeStage)],
            value=E91
        )
        
        # Task Selection (commented out as in original)
        self.selectedtask = widgets.RadioButtons(
            options=[('Generate a secure key', generate_key),
                    ('Send a Message via Classical Channel', send_message),
                    ('Send a Message via Quantum Channel(only for 3 Stage Protocol)', send_message_quantum)],
            value=generate_key
        )
        
        # Message Input
        self.message_var = widgets.Text(
            description='Enter message:',
            style={'description_width': 'initial'}
        )
        
        # Key Input
        self.key_var = widgets.Text(
            description='Enter secure key (binary):',
            style={'description_width': 'initial'}
        )
        
        # Grid Size
        self.name_var = widgets.IntText(
            value=5,
            description='Enter grid size:',
            style={'description_width': 'initial'}
        )
        
        # Submit Button
        submit_btn = widgets.Button(
            description='Submit',
            button_style='primary'
        )
        submit_btn.on_click(self.onSubmit)
        
        # Layout
        main_container = widgets.VBox([
            title,
            widgets.VBox([self.ksu_id_var], layout=widgets.Layout(margin='20px 0px')),
            mode_label,
            widgets.VBox([self.selectedMode], layout=widgets.Layout(margin='10px 0px 20px 35px')),
            protocol_label,
            widgets.VBox([self.selectedProtocol], layout=widgets.Layout(margin='10px 0px 20px 35px')),
            widgets.VBox([self.name_var], layout=widgets.Layout(margin='20px 0px')),
            widgets.HBox([submit_btn], layout=widgets.Layout(margin='20px 0px'))
        ])
        self.window.append_display_data(main_container)
        display(self.window)
    
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
    
    def onSubmit(self, button):
        # Note: Instead of destroying window, we'll handle this differently in Jupyter
        # instance = QNetwork(self)
        network = QNetwork(self.selectedMode.value, self.selectedProtocol.value, self.message_var.value, self.ksu_id_var.value, self.name_var.value)
        # self.window.append_display_data(network.display())
        # display(network.display())
        with self.window:
            self.window.clear_output()
            self.window.outputs = []
            display(network.display())

# Create instance
game_instance = Home()