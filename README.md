# Meshtastic Home Node Direct MessageCoverage Map

A real-time coverage mapping tool to measure the 3-hop coverage area for a Meshtastic node. This application listens for direct messages from Meshtastic nodes containing GPS coordinates and visualizes the network coverage area on a live interactive map.

## Preamble
Most implementations I've seen only measure the coverage of one node instead of using the entire mesh to reach a target node. I wanted to make a coverage map for my Meshtastic network that reflected real-world use. By using direct messages as the basis of the location packets I could hop over several nodes in the local mesh to reach my home node. 

## Development Environment
I connected a Heltec V3 Meshtastic node using USB to an Ubuntu Linux machine and executed run.sh. I have a LilyGo Lora32 2.1/1.6 in my attic connected to a 8dB roof antenna over 16 ft of low loss cable. I then paired my iPhone to another Heltec V3 and ran this custom Shortcut script to automatically send location data to a target node every 15 seconds for 20 minutes. The node name must be converted from Hexadecimal: https://www.icloud.com/shortcuts/9051a51160d64fee94757ffa2fdd02bd You'll have to approve location permissions when you run the Shortcut if you use this. In my setup I'm actually measuring 2-hop distance for my home node because all distant messages are going to be routed through that roof node to get to the target node connected to my computer.

## Features

- Real-time monitoring of Meshtastic direct messages via USB
- Automatic parsing of GPS coordinates from messages
- Interactive map visualization with OpenStreetMap
- Real-time updates via WebSockets
- Coverage area visualization as a semi-transparent green polygon
- Persistent data storage in JSON format

## Requirements

- Python 3.x
- Meshtastic device connected via USB
- Python packages (see requirements.txt):
  - meshtastic
  - fastapi
  - uvicorn
  - scipy
  - numpy

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/mesh-dm-map.git
   cd mesh-dm-map
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Connect your Meshtastic device via USB

2. Start the server:
   ```
   python server.py
   ```

3. Open a web browser and navigate to:
   ```
   http://localhost:8300
   ```

4. The map will automatically update as new location messages are received from Meshtastic nodes.

## Message Format

The application expects messages in the following format:
```
TIME
LAT, LONG
ELEVATION
```

Example:
```
11:11 PM
43.25647400901538, -84.41694492129633
302.8 Meters
```

## How It Works

1. The Python backend connects to a Meshtastic device via USB and listens for incoming direct messages.
2. When a message is received, it is parsed to extract GPS coordinates.
3. The coordinates are stored in a JSON file and used to calculate the coverage area using a convex hull algorithm.
4. The web interface displays the points and coverage area on an interactive map.
5. WebSockets are used to push real-time updates to connected clients.

## Project Structure

```
mesh-dm-map/
├── server.py           # Main Python server
├── requirements.txt    # Python dependencies
├── data/
│   └── points.json     # Data storage
└── static/
    ├── index.html      # Web interface
    ├── app.js          # Frontend JavaScript
    └── style.css       # CSS styling
```

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
