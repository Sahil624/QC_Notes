# Notebook Generator Installation Instructions

### Install Python

**Install Python 3.11:** Download Python from python.org or via the Microsoft Store. Make sure to add Python to your system PATH during installation.

### Download and Extract the Project

**Download the project:** Go to Qiselab9 QC_Notes GitHub repository, click on "Code", and select "Download ZIP". Extract the downloaded ZIP file to a directory with a short path to avoid issues, especially on Windows.

### Open Terminal and Navigate

**Open Terminal (Command Prompt):** Navigate to the QC_Notes folder where you extracted the ZIP file using the cd command:

`cd path/to/QC_Notes`

### Install Dependencies

**Install dependencies using requirements.txt:** Run the following command to install required Python packages:

`pip install -r requirements.txt`

If the above command doesn't work, install dependencies manually with the following commands:

`pip install jupyter notebook jupyterlab qutip matplotlib`<br>
`pip install qiskit==0.45.2 qiskit-aer==0.14.2`

### Run JupyterLab

**Start JupyterLab:** After installing dependencies, launch JupyterLab by running the command:

`jupyter lab`<br>
This will open JupyterLab in your default web browser. If it doesn't open follow the instructions from command prompt.

### Generate Notebooks

**Run Course_Generator.ipynb:** In JupyterLab, open Course_Generator.ipynb. Execute the notebook to generate your desired notebooks.

### Locate Generated Notebooks

**Find generated notebooks:** Once generated, the notebooks will be available at /Modules/Course.ipynb.
