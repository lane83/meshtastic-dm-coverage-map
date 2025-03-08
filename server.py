#!/usr/bin/env python3
import meshtastic
import meshtastic.serial_interface
import json
import time
import re
import os
import asyncio
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from scipy.spatial import ConvexHull
import numpy as np
import uvicorn
import threading

# Initialize FastAPI
app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Data store
DATA_FILE = "data/points.json"

# Ensure data directory exists
os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

# Initialize data file if it doesn't exist
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({"points": [], "coverage": []}, f)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections = []
    
    async def connect(self, websocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    async def disconnect(self, websocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def broadcast(self, message):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                # Connection might be closed
                pass

manager = ConnectionManager()

# Parse message function
def parse_message(message):
    # Extract coordinates using regex pattern
    # Format: "TIME\nLAT, LONG\nELEVATION"
    pattern = r'(?:[0-9:]+\s*(?:AM|PM))?[^\n]*\n([0-9.-]+),\s*([0-9.-]+)'
    match = re.search(pattern, message)
    if match:
        lat = float(match.group(1))
        lon = float(match.group(2))
        return lat, lon
    return None

# Calculate convex hull from points
def calculate_coverage_area(points):
    if len(points) < 3:
        return points  # Not enough points for a polygon
    
    try:
        # Calculate convex hull
        points_array = np.array(points)
        hull = ConvexHull(points_array)
        hull_points = [points_array[i].tolist() for i in hull.vertices]
        return hull_points
    except Exception as e:
        print(f"Error calculating convex hull: {e}")
        return []

# Load data from file
def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"points": [], "coverage": []}

# Save data to file
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# Add a new point and update coverage
async def add_point(lat, lon):
    data = load_data()
    
    # Create new point
    point = {
        "lat": lat,
        "lon": lon,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Add to points list
    data["points"].append(point)
    
    # Update coverage area if we have enough points
    if len(data["points"]) >= 3:
        points_array = [[p["lat"], p["lon"]] for p in data["points"]]
        data["coverage"] = calculate_coverage_area(points_array)
    
    # Save updated data
    save_data(data)
    
    # Broadcast update to all connected clients
    await manager.broadcast(data)
    
    return data

# Meshtastic message handler
def on_message_received(packet, interface):
    try:
        # Extract message text
        if packet.get("decoded", {}).get("text"):
            message = packet["decoded"]["text"]
            print(f"Received message: {message}")
            
            # Parse coordinates
            coords = parse_message(message)
            if coords:
                lat, lon = coords
                print(f"Extracted coordinates: {lat}, {lon}")
                
                # Add point and update coverage (in async context)
                asyncio.run(add_point(lat, lon))
    except Exception as e:
        print(f"Error processing message: {e}")

class MeshtasticListener:
    def __init__(self):
        self.interface = None
        self.connected = False
        
    def connect(self):
        try:
            # Set up message handler using pub/sub
            meshtastic.pub.subscribe(on_message_received, "meshtastic.receive")
            
            # Connect to Meshtastic device via USB
            self.interface = meshtastic.serial_interface.SerialInterface()
            self.connected = True
            print("Connected to Meshtastic device")
        except Exception as e:
            print(f"Error connecting to Meshtastic device: {e}")
            self.connected = False

# Start Meshtastic listener in a separate thread
def start_meshtastic_listener():
    listener = MeshtasticListener()
    while True:
        if not listener.connected:
            try:
                listener.connect()
            except Exception as e:
                print(f"Error connecting to Meshtastic: {e}")
            
        # Wait before trying to reconnect if needed
        time.sleep(10)

# API routes
@app.get("/")
async def root():
    return FileResponse("static/index.html")

@app.get("/data")
async def get_data():
    return load_data()

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and wait for messages
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(websocket)

# Main function
if __name__ == "__main__":
    # Start Meshtastic listener in background thread
    threading.Thread(target=start_meshtastic_listener, daemon=True).start()
    
    # Run web server
    uvicorn.run(app, host="0.0.0.0", port=8300)
