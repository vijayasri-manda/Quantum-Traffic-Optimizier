import streamlit as st
from streamlit_searchbox import st_searchbox
import googlemaps
import networkx as nx
import folium
from streamlit_folium import folium_static
from quantum_optimizer import QuantumRouteOptimizer
import pandas as pd
import requests

# Page configuration
st.set_page_config(page_title="Quantum Traffic Optimizer", page_icon="🚗", layout="wide")

# Title
st.title("🚗 Quantum Traffic Optimization System")
st.markdown("Real-time route optimization using quantum-inspired algorithms and Google Maps data")

# API Key (global for use in search functions)
API_KEY = "AIzaSyAAOTEY2oQj749gyg3OPeNdztJg_mVWV80"

# Function to get place suggestions from Google Places API
def search_locations(searchterm: str):
    """Dynamic location search using Google Places API"""
    if not searchterm or len(searchterm) < 2:
        return []
    
    try:
        url = "https://maps.googleapis.com/maps/api/place/autocomplete/json"
        params = {
            'input': searchterm,
            'key': API_KEY,
        }
        response = requests.get(url, params=params, timeout=2)
        data = response.json()
        
        if data.get('status') == 'OK':
            suggestions = []
            for prediction in data.get('predictions', [])[:8]:
                suggestions.append(prediction['description'])
            return suggestions
        return []
    except Exception as e:
        return []

# Sidebar for API key and inputs
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Google Maps API Key", type="password", value=API_KEY)
    
    # Update global API key
    if api_key:
        API_KEY = api_key
    
    st.header("📍 Route Details")
    
    # Start Location with dynamic searchbox
    st.markdown("### 🚀 Start Location")
    start_location = st_searchbox(
        search_locations,
        key="start_location_search",
        placeholder="🔍 Type location (e.g., Gudivada, Mumbai, New York)...",
        default="New York, NY"
    )
    
    if start_location:
        st.success(f"📍 **From:** {start_location}")
    
    st.markdown("---")
    
    # Destination with dynamic searchbox
    st.markdown("### 🏁 Destination")
    end_location = st_searchbox(
        search_locations,
        key="end_location_search",
        placeholder="🔍 Type location (e.g., Hyderabad, Delhi, Boston)...",
        default="Boston, MA"
    )
    
    if end_location:
        st.success(f"🏁 **To:** {end_location}")
    
    st.markdown("---")
    
    # Display selected route
    if start_location and end_location:
        st.info(f"**Route:** {start_location} → {end_location}")
    
    st.markdown("---")
    
    optimize_button = st.button("🔍 Find Optimal Route", type="primary", use_container_width=True)

def get_all_routes(gmaps, origin, destination):
    """Fetch all available routes from Google Maps"""
    try:
        directions = gmaps.directions(
            origin, 
            destination, 
            mode="driving", 
            alternatives=True, 
            departure_time="now",
            traffic_model="best_guess"
        )
        
        if not directions:
            return None
        
        all_routes = []
        
        for route_idx, route in enumerate(directions):
            legs = route['legs'][0]
            
            # Extract route coordinates
            route_coords = []
            for step in legs['steps']:
                start_loc = step['start_location']
                route_coords.append([start_loc['lat'], start_loc['lng']])
            # Add final point
            end_loc = legs['steps'][-1]['end_location']
            route_coords.append([end_loc['lat'], end_loc['lng']])
            
            # Extract metrics
            distance_meters = legs['distance']['value']
            duration_seconds = legs['duration']['value']
            
            # Get traffic duration if available
            if 'duration_in_traffic' in legs:
                duration_in_traffic_seconds = legs['duration_in_traffic']['value']
            else:
                duration_in_traffic_seconds = duration_seconds
            
            traffic_delay_seconds = max(0, duration_in_traffic_seconds - duration_seconds)
            
            route_info = {
                'route_id': route_idx,
                'route_name': route.get('summary', f'Route {route_idx + 1}'),
                'coordinates': route_coords,
                'distance_km': distance_meters / 1000,
                'distance_meters': distance_meters,
                'duration_min': duration_seconds / 60,
                'duration_seconds': duration_seconds,
                'duration_in_traffic_min': duration_in_traffic_seconds / 60,
                'duration_in_traffic_seconds': duration_in_traffic_seconds,
                'traffic_delay_min': traffic_delay_seconds / 60,
                'traffic_delay_seconds': traffic_delay_seconds,
                'start_address': legs['start_address'],
                'end_address': legs['end_address']
            }
            
            all_routes.append(route_info)
        
        return all_routes
    
    except Exception as e:
        st.error(f"Error fetching routes: {str(e)}")
        return None

def create_map_with_all_routes(all_routes, optimal_route_id, start_location, end_location):
    """Create interactive map showing all routes with optimal highlighted"""
    if not all_routes:
        return None
    
    # Center map on start location
    center = all_routes[0]['coordinates'][0]
    m = folium.Map(location=center, zoom_start=8)
    
    # Define colors for routes
    route_colors = ['gray', 'lightgray', 'darkgray', 'purple', 'orange']
    
    # Add all routes to map
    for route in all_routes:
        route_id = route['route_id']
        coords = route['coordinates']
        
        # Check if this is the optimal route
        is_optimal = (route_id == optimal_route_id)
        
        if is_optimal:
            color = 'green'
            weight = 7
            opacity = 1.0
            dash_array = None
            label = f"⭐ OPTIMAL: {route['route_name']}"
        else:
            color = route_colors[route_id % len(route_colors)]
            weight = 4
            opacity = 0.6
            dash_array = '10, 5'
            label = f"Route {route_id + 1}: {route['route_name']}"
        
        # Create popup with route details
        popup_html = f"""
        <div style="font-family: Arial; width: 250px;">
            <h4 style="margin: 0; color: {'green' if is_optimal else 'black'};">
                {'⭐ OPTIMAL ROUTE' if is_optimal else f'Route {route_id + 1}'}
            </h4>
            <hr style="margin: 5px 0;">
            <b>Name:</b> {route['route_name']}<br>
            <b>Distance:</b> {route['distance_km']:.2f} km<br>
            <b>Travel Time:</b> {route['duration_in_traffic_min']:.1f} min
        </div>
        """
        
        folium.PolyLine(
            coords,
            color=color,
            weight=weight,
            opacity=opacity,
            dash_array=dash_array,
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=label
        ).add_to(m)
    
    # Add start marker
    folium.Marker(
        center,
        popup=f"<b>START</b><br>{start_location}",
        tooltip="Start Location",
        icon=folium.Icon(color='green', icon='play', prefix='fa')
    ).add_to(m)
    
    # Add end marker
    end_coord = all_routes[0]['coordinates'][-1]
    folium.Marker(
        end_coord,
        popup=f"<b>DESTINATION</b><br>{end_location}",
        tooltip="Destination",
        icon=folium.Icon(color='red', icon='stop', prefix='fa')
    ).add_to(m)
    
    return m

# Main application logic
if optimize_button:
    if not api_key:
        st.error("⚠️ Please enter your Google Maps API Key")
    elif not start_location or not end_location:
        st.error("⚠️ Please enter both start and destination locations")
    else:
        with st.spinner("🔄 Fetching all available routes from Google Maps..."):
            try:
                # Initialize Google Maps client
                gmaps = googlemaps.Client(key=api_key)
                
                # Get all routes
                all_routes = get_all_routes(gmaps, start_location, end_location)
                
                if not all_routes:
                    st.error("❌ No routes found. Please check your locations and API key.")
                else:
                    st.success(f"✅ Found {len(all_routes)} alternative routes!")
                    
                    # Display all routes in a detailed table
                    st.header("🛣️ ALL AVAILABLE ROUTES FROM SOURCE TO DESTINATION")
                    
                    # Create DataFrame for display
                    route_table_data = []
                    for route in all_routes:
                        route_table_data.append({
                            "Route #": route['route_id'] + 1,
                            "Route Name": route['route_name'],
                            "Distance (km)": f"{route['distance_km']:.2f}",
                            "Travel Time (min)": f"{route['duration_in_traffic_min']:.1f}"
                        })
                    
                    df = pd.DataFrame(route_table_data)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    
                    # Apply quantum optimization
                    st.header("⚛️ QUANTUM OPTIMIZATION")
                    
                    # Quantum optimization with timing
                    import time
                    with st.spinner("Applying Grover's algorithm to find optimal route..."):
                        quantum_start = time.time()
                        optimizer = QuantumRouteOptimizer(all_routes)
                        optimal_route_id, optimal_route = optimizer.find_optimal_route()
                        quantum_time = time.time() - quantum_start
                    
                    if optimal_route:
                        st.success("✅ Quantum optimization complete!")
                        st.info(f"⏱️ Computation Time: {quantum_time*1000:.2f} ms")
                        
                        # Display optimal route details prominently
                        st.header("⭐ OPTIMAL ROUTE ")
                        st.success(f"🏆 This route has the best balance of SHORT DISTANCE and LOW TIME!")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric(
                                label="Route",
                                value=f"#{optimal_route['route_id'] + 1}"
                            )
                        
                        with col2:
                            st.metric(
                                label="Distance",
                                value=f"{optimal_route['distance_km']:.2f} km"
                            )
                        
                        with col3:
                            st.metric(
                                label="Travel Time",
                                value=f"{optimal_route['duration_in_traffic_min']:.1f} min"
                            )
                        
                        # Display route name
                        st.info(f"**Route Name:** {optimal_route['route_name']}")
                        
                        # Comparison with other routes
                        st.subheader("📊 Comparison with Other Routes")
                        
                        comparison_data = []
                        for route in all_routes:
                            is_optimal = route['route_id'] == optimal_route_id
                            comparison_data.append({
                                "Status": "⭐ OPTIMAL" if is_optimal else "Alternative",
                                "Route": f"Route {route['route_id'] + 1}",
                                "Name": route['route_name'],
                                "Distance (km)": f"{route['distance_km']:.2f}",
                                "Travel Time (min)": f"{route['duration_in_traffic_min']:.1f}",
                                "Difference": f"+{route['duration_in_traffic_min'] - optimal_route['duration_in_traffic_min']:.1f} min, +{route['distance_km'] - optimal_route['distance_km']:.2f} km" if not is_optimal else "—"
                            })
                        
                        comparison_df = pd.DataFrame(comparison_data)
                        st.dataframe(comparison_df, use_container_width=True, hide_index=True)
                        
                        # Map visualization
                        st.header("🗺️ ROUTE VISUALIZATION")
                        st.markdown("""
                        **Legend:**
                        - 🟢 **Green (Solid)** = Optimal Route (Selected by Quantum Algorithm)
                        - ⚪ **Gray (Dashed)** = Alternative Routes
                        - 🟢 **Green Marker** = Start Location
                        - 🔴 **Red Marker** = Destination
                        """)
                        
                        map_obj = create_map_with_all_routes(all_routes, optimal_route_id, start_location, end_location)
                        if map_obj:
                            folium_static(map_obj, width=1400, height=700)
                        
                        # Detailed explanation
                        with st.expander("💡 Why This Route is Optimal"):
                            st.markdown(f"""
                            ### Optimization Details
                            
                            **Selected Route:** Route {optimal_route['route_id'] + 1} - {optimal_route['route_name']}
                            
                            **Key Metrics:**
                            - **Total Distance:** {optimal_route['distance_km']:.2f} km
                            - **Travel Time:** {optimal_route['duration_in_traffic_min']:.1f} minutes
                            
                            **Optimization Method:**
                            - Algorithm: Quantum-inspired Grover's Search Algorithm
                            - **Optimization Goal:**
                            - Evaluation Criteria: Time with traffic (50% weight) + Distance (50% weight)
                            - Computation Time: {quantum_time*1000:.2f} milliseconds
                            
                            **Why This Route?**
                            This route was selected because it provides the **BEST BALANCE** of short distance and low travel time. 
                            Among all {len(all_routes)} available routes, this one optimizes both factors equally:
                            - **Distance:** {optimal_route['distance_km']:.2f} km
                            - **Travel Time:** {optimal_route['duration_in_traffic_min']:.1f} minutes
                            
                            **Comparison with Other Routes:**
                            """)
                            
                            # Show comparison with other routes
                            for route in all_routes:
                                if route['route_id'] != optimal_route_id:
                                    time_diff = route['duration_in_traffic_min'] - optimal_route['duration_in_traffic_min']
                                    dist_diff = route['distance_km'] - optimal_route['distance_km']
                                    st.write(f"- **Route {route['route_id'] + 1}:** {route['distance_km']:.2f} km, {route['duration_in_traffic_min']:.1f} min (Difference: {dist_diff:+.2f} km, {time_diff:+.1f} min)")
                            
                            st.success(f"✅ This route optimizes BOTH distance and time for the best overall journey!")
                        
                        # Route details
                        with st.expander("📋 Detailed Route Information"):
                            st.write(f"**Start Address:** {optimal_route['start_address']}")
                            st.write(f"**End Address:** {optimal_route['end_address']}")
                            st.write(f"**Total Waypoints:** {len(optimal_route['coordinates'])}")
                    
                    else:
                        st.error("❌ Could not determine optimal route")
            
            except googlemaps.exceptions.ApiError as e:
                st.error(f"❌ Google Maps API Error: {str(e)}")
                st.info("💡 Make sure your API key has Directions API enabled and billing is set up")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                import traceback
                st.code(traceback.format_exc())

# Information section
with st.expander("ℹ️ About This System"):
    st.markdown("""
    ### How It Works
    
    1. **Data Collection**: Fetches ALL available routes with real-time traffic data from Google Maps API
    2. **Route Analysis**: Extracts distance and time for each route
    3. **Quantum Optimization**: Applies Grover's algorithm-inspired search to find optimal path
    4. **Visualization**: Displays all routes on map with optimal route highlighted in green
    
    ### Technologies Used
    - **Qiskit**: Quantum circuit simulation
    - **Google Maps API**: Real-time traffic data & Places autocomplete
    - **NetworkX**: Graph algorithms
    - **Streamlit**: Web interface
    - **Folium**: Interactive map visualization
    - **Streamlit-Searchbox**: Real-time location autocomplete
    
    ### Metrics Explained
    - **Distance**: Total length of the route in kilometers
    - **Travel Time**: Estimated travel time considering current traffic conditions
    """)
