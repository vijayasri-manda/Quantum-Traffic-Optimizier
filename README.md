# Quantum Traffic Optimization System

Real-time route optimization using quantum-inspired algorithms and Google Maps data.

## Features

- ✅ Real-time traffic data from Google Maps
- ✅ Quantum-inspired optimization using Grover's algorithm
- ✅ Interactive web interface with Streamlit
- ✅ Visual route display on interactive maps
- ✅ Multiple route comparison

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Google Maps API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the following APIs:
   - Directions API
   - Distance Matrix API
   - Maps JavaScript API
4. Create credentials (API Key)
5. Copy your API key

### 3. Run the Application

```bash
streamlit run app.py
```

### 4. Use the System

1. Enter your Google Maps API key in the sidebar
2. Input start location (e.g., "New York, NY")
3. Input destination (e.g., "Boston, MA")
4. Click "Find Optimal Route"
5. View the optimized route on the map

## Project Structure

```
VIT Quantum HAckthon/
├── app.py                  # Main Streamlit application
├── quantum_optimizer.py    # Quantum optimization logic
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## How It Works

### 1. Data Collection
- Fetches real-time traffic data using Google Maps Directions API
- Retrieves multiple alternative routes with current traffic conditions

### 2. Graph Construction
- Models road network as a directed graph
- Nodes represent intersections/waypoints
- Edges represent road segments with traffic-based weights

### 3. Quantum-Inspired Optimization
- Implements Grover's algorithm simulation using Qiskit
- Searches through candidate paths in superposition
- Amplifies probability of optimal solution

### 4. Route Visualization
- Displays optimal route on interactive Folium map
- Shows start/end markers and route polyline
- Provides time and distance metrics

## Technologies

| Technology | Purpose |
|------------|---------|
| Python | Backend programming |
| Qiskit | Quantum circuit simulation |
| Google Maps API | Real-time traffic data |
| NetworkX | Graph modeling |
| Streamlit | Web interface |
| Folium | Map visualization |

## Applications

- 🏙️ Smart city traffic management
- 🚗 Navigation systems
- 📦 Logistics route optimization
- 🚑 Emergency vehicle routing
- 🚕 Ride-sharing optimization

## Advantages

- Uses real-time traffic information
- Demonstrates quantum computing concepts
- Finds more efficient routes than classical methods
- Scalable for smart city implementations

## Future Enhancements

- Multi-destination route optimization
- Historical traffic pattern analysis
- Integration with IoT traffic sensors
- Real quantum hardware deployment
- Machine learning for traffic prediction

## License

MIT License

## Contributors

VIT Quantum Hackathon Team
