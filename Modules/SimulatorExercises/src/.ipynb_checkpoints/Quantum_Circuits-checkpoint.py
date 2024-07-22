from qiskit import QuantumCircuit, QuantumRegister, Aer
#from qiskit_aer.aerprovider import AerSimulator as Aer
from qiskit.quantum_info import Statevector, partial_trace
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from qiskit.visualization import plot_state_qsphere
import numpy as np
from numpy.random import randint
from qiskit.extensions import UnitaryGate
from qiskit.circuit.library import IGate  

quantumcirc= None
window_local = None
canvas_widget = None
save1 = None
save2 = None
save3 = None
counter = 1

def make_entanglement(quantumcirc, a, b):
    quantumcirc.h(a)
    quantumcirc.cx(a, b)

def final_qubit_state(stateVector, matrix):
    """Get the statevector for the first qubit, discarding the rest."""
    # get the full statevector of all qubits
    full_statevector = stateVector

    # get the density matrix for the first qubit by taking the partial trace
    partial_density_matrix = partial_trace(full_statevector, matrix)

    # extract the statevector out of the density matrix
    partial_statevector = np.diagonal(partial_density_matrix)

    return partial_statevector

def create_or_reload_canvas(new_fig, col):
    global canvas_widget
    # Clear the existing canvas
    if canvas_widget:
        canvas_widget.get_tk_widget().destroy()

    # Create a new FigureCanvasTkAgg widget with the new figure
    window_local = FigureCanvasTkAgg(new_fig)
    window_local.get_tk_widget().grid(row=col, column=4) 
    # window_local = FigureCanvasTkAgg(new_fig)
    # window_local.get_tk_widget().grid(row=col, column=5) 

def intialize_circuit(window):
    global window_local
    window_local = window
    quantumcirc = QuantumCircuit()
    return quantumcirc

def BinaryToDecimal(binary): 
    binary1 = binary 
    decimal, i, n = 0, 0, 0
    while(binary != 0): 
        dec = binary % 10
        decimal = decimal + dec * pow(2, i) 
        binary = binary//10
        i += 1
    return (decimal)    

def BinarytoString(binary):  
    str_data =' '
    binary_data=''.join([str(item) for item in binary])
    str_data =  ''.join(chr(int(binary_data[i:i+8], 2)) for i in range(0, len(binary_data), 8))
    return str_data

def E91_encode_message(bits, bases, n, number_of_nodes, angles_A):
    message = []
    for i in range(n):
        number_of_qubits = number_of_nodes*2
        qc = QuantumCircuit(number_of_qubits, 2)
        
        create_entanglement(qc, number_of_nodes)
    
        qc.ry(2 * angles_A[bases[i]], 0)
        message.append(qc)
    return message

def E91_measure_message(message, bases, n, angles_B, number_of_nodes):
    a_measurements = []
    b_measurements = []
    for q in range(n):
        message[q].ry(2 * angles_B[bases[q]], number_of_nodes*2 -1)
        message[q].measure(0, 0)
        message[q].measure(number_of_nodes*2 -1, 1)
        aer_sim = Aer.get_backend('aer_simulator')
        result = aer_sim.run(message[q], shots=1, memory=True).result()
        measured_bit = result.get_memory()[0]
        a_measurements.append(int(measured_bit[0]))
        b_measurements.append(int(measured_bit[1]))
    return [a_measurements, b_measurements]

def remove_garbage(a_bases, b_bases, bits, n):
    good_bits = []
    for q in range(n):
        if a_bases[q] == b_bases[q]:
            good_bits.append(bits[q])
    return good_bits

def E91_key_generation(number_of_nodes, window):
    np.random.seed(seed=0)
    n = 50

    angles_A = [0, np.pi / 4, np.pi / 2]
    angles_B = [0, np.pi / 4, np.pi / 2]
    # Alice generates bits
    alice_bits = randint(2, size=n)

    ## Step 2
    # Create an array to tell us which qubits
    # are encoded in which bases
    alice_bases = randint(2, size=n)
    message = E91_encode_message(alice_bits, alice_bases, n, number_of_nodes, angles_A)

    bob_bases = randint(2, size=n)
    [alice_results, bob_results] = E91_measure_message(message, bob_bases, n, angles_B, number_of_nodes)
    alice_key = remove_garbage(alice_bases, bob_bases, alice_results, n)
    bob_key = remove_garbage(alice_bases, bob_bases, bob_results,n)
    return ''.join(map(str, bob_key))


def building_circuit(number_of_nodes, window):
    quantumcirc = intialize_circuit(window)
    qr = QuantumRegister(number_of_nodes*2)
    quantumcirc.add_register(qr)
    create_entanglement(quantumcirc, number_of_nodes)
    print(quantumcirc)
    return E91_key_generation(number_of_nodes, window)

def create_entanglement(quantumcirc, number_of_nodes):
    # number_of_qubits = number_of_nodes*2
    for index in range(number_of_nodes):
        quantumcirc.h(index*2)
        quantumcirc.cx(index*2, index*2 + 1)

    for index in range(number_of_nodes):
        if(index>0):
            quantumcirc.barrier(index*2, index*2-1)
            quantumcirc.cx(index*2-1, index*2)
            quantumcirc.h(index*2-1)
            quantumcirc.barrier(index*2, index*2-1)

    for qubit in range(1,number_of_nodes*2-2,2):
        quantumcirc.cz(qubit, 0)
        quantumcirc.cx(qubit+1, number_of_nodes*2-1)

def is_unitary(m):
    """Check if the matrix is unitary."""
    return np.allclose(np.eye(m.shape[0]), m @ m.conj().T)

def generate_unitary():
    """Generate a 2x2 unitary diagonal matrix."""
    angle = np.random.rand() * 2 * np.pi
    return np.array([[np.exp(1j * angle), 0],
                     [0, np.exp(-1j * angle)]])

def unitary_error(scaling_factor):
    E=np.array([[scaling_factor, 0],
                     [0, scaling_factor]])
    return E

def calculate_gamma(alpha, L): #decoherence probability
    return 10**(-alpha*L/10)

def threestage_encode_message(bits, U_A, U_B, n):
    message = []
    for i in range(n):  # Loop over each bit
        qc = QuantumCircuit(1, 1)
        # Prepare qubit in Z-basis
        if bits[i] == 0:
            pass
        else:
            qc.x(0)
        # Apply custom unitary operations and identity gates shows a transmission from one node to other. 
        qc.append(UnitaryGate(U_A, label='U_A'), [0])
        qc.append(IGate(), [0])
        qc.append(UnitaryGate(U_B, label='U_B'), [0])
        qc.append(IGate(), [0])
        qc.append(UnitaryGate(np.conjugate(U_A).T, label='U_A†'), [0])
        qc.append(IGate(), [0])
        qc.append(UnitaryGate(np.conjugate(U_B).T, label='U_B†'), [0])
        qc.barrier()

        # Append the quantum circuit for this qubit
        message.append(qc)
    return message

def threestage_decode_message(encoded_message, n):
    # Initialize the main list to store decoded qubits for each bit
    # decoded_message = [[] for _ in range(n)]
    decoded_message = []
    # Define the backend to simulate the quantum circuit
    backend = Aer.get_backend('qasm_simulator')


    for i, qc in enumerate(encoded_message):
        # Add a measurement operation to the circuit
        qc.measure(0, 0)
        result = backend.run(qc, shots=1, memory=True).result()
        measured_bit = result.get_memory()[0]
        decoded_message.append(measured_bit)
    return ''.join(map(str, decoded_message))

def threestage_key_generation(number_of_nodes):
    U_A = generate_unitary()
    U_B = generate_unitary()
    n =50
    bits = randint(2, size=n)

    # Encode the message
    message = threestage_encode_message(bits, U_A, U_B, n)
    decoded_message = threestage_decode_message(message, n )
    return decoded_message

def threestage_message_transmission(bits):
    U_A = generate_unitary()
    U_B = generate_unitary()
    n = len(bits)
    bits = [int(char) for char in bits]

    # Encode the message
    message = threestage_encode_message(bits, U_A, U_B, n)
    decoded_message = threestage_decode_message(message, n )
    return decoded_message
    