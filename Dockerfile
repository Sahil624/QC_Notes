# Use official Python image as base
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies including X11 and Tkinter
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    python3-tk \
    libx11-6 \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install \
    jupyter \
    notebook \
    jupyterlab \
    qutip \
    matplotlib \
    qiskit==0.45.2 \
    qiskit-aer==0.14.2

# Create directory for notebooks
WORKDIR /app

# Copy all contents from the current directory
COPY . .

# Expose Jupyter port
EXPOSE 8888

# Start Jupyter Lab
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=''"]