# Docker Setup Instructions for Jupyter Environment with GUI Support

## Prerequisites
1. Install Docker and Docker Compose on your system:
   - [Docker for Windows](https://docs.docker.com/desktop/install/windows-install/)
   - [Docker for Mac](https://docs.docker.com/desktop/install/mac-install/)
   - [Docker for Linux](https://docs.docker.com/engine/install/)
   - [Docker Compose Installation](https://docs.docker.com/compose/install/)

## Setup Instructions

1. Clone the repository:
```bash
git clone git@github.com:Sahil624/QC_Notes.git
cd QC_Notes
git checkout origin/docker-file
```

2. Start the containers (This will take few minutes to run):
```bash
docker-compose up --build
```

## Usage Instructions

1. Access Jupyter Lab:
   - Open your web browser and go to: `http://localhost:8888`
   - You'll see the Jupyter Lab interface with your notebooks

2. For viewing the simulation in Learning Object "22.4 The E91 Protocol":
   - Before running the simulation cells, open a new browser tab and go to: `http://localhost:8080/vnc.html`
   - Keep this tab open while running the simulation cells
   - The simulation will appear in this virtual desktop window
   - If you don't open this window before running the simulation, you won't be able to see the visualization

## How it Works
- The setup uses two containers:
  1. Jupyter container: Runs your notebooks and Tkinter applications
  2. noVNC container: Provides the virtual display server and web interface
- The simulation in LO 22.4 will display its GUI in the noVNC window

## Troubleshooting

1. If you can't see the simulation:
   - Make sure you opened `http://localhost:8080` before running the simulation cells
   - Keep the noVNC tab open while running the simulation
   - Try rerunning the notebook cells
   - If still not working, restart the Jupyter kernel and try again

2. If ports are already in use, modify the port mappings in docker-compose.yml:
```yaml
ports:
  - "8889:8888"  # For Jupyter
  - "8081:8080"  # For noVNC
```

3. If containers don't start properly:
```bash
# Check container logs
docker-compose logs

# Rebuild containers
docker-compose up --build --force-recreate
```

4. To stop the containers:
```bash
docker-compose down
```

## Common Commands
```bash
# Start containers in background
docker-compose up -d

# View container logs
docker-compose logs -f

# Stop containers
docker-compose down

# Rebuild and restart containers
docker-compose up --build --force-recreate
```