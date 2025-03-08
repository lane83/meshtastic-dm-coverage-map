// Initialize map
const map = L.map('map').setView([0, 0], 2);  // Default view, will be updated

// Add OpenStreetMap tile layer
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

// Variables to store data and map elements
let points = [];
let coveragePolygon = null;
let pointsLayer = L.layerGroup().addTo(map);

// Connect to WebSocket for real-time updates
const socket = new WebSocket(`ws://${window.location.host}/ws`);
const statusElement = document.getElementById('connection-status');
const lastUpdateElement = document.getElementById('last-update');

// WebSocket event handlers
socket.onopen = () => {
    statusElement.textContent = 'Connected';
    statusElement.className = 'connected';
    
    // Get initial data
    fetchData();
};

socket.onclose = () => {
    statusElement.textContent = 'Disconnected';
    statusElement.className = 'disconnected';
    
    // Try to reconnect after a delay
    setTimeout(() => {
        window.location.reload();
    }, 5000);
};

socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    updateMap(data);
    lastUpdateElement.textContent = new Date().toLocaleString();
};

// Fetch initial data
function fetchData() {
    fetch('/data')
        .then(response => response.json())
        .then(data => {
            updateMap(data);
        })
        .catch(error => console.error('Error fetching data:', error));
}

// Update map with new data
function updateMap(data) {
    // Update points array
    points = data.points || [];
    
    // Clear existing points
    pointsLayer.clearLayers();
    
    // We're not displaying individual waypoints anymore, only the coverage area
    // points.forEach(point => {
    //     const marker = L.marker([point.lat, point.lon]).addTo(pointsLayer);
    //     marker.bindPopup(`Lat: ${point.lat}, Lon: ${point.lon}<br>Time: ${point.time}`);
    // });
    
    // Update coverage polygon
    if (coveragePolygon) {
        map.removeLayer(coveragePolygon);
    }
    
    const coverage = data.coverage || [];
    if (coverage.length > 2) {
        coveragePolygon = L.polygon(coverage, {
            color: 'green',
            fillColor: 'green',
            fillOpacity: 0.3
        }).addTo(map);
    }
    
    // Fit map to bounds if there are points
    if (points.length > 0) {
        const latLngs = points.map(p => [p.lat, p.lon]);
        map.fitBounds(L.latLngBounds(latLngs));
    }
}
